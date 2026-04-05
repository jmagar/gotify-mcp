# Common MCP Code Patterns

Reusable patterns in the gotify-mcp implementation.

## Action dispatch

The canonical routing pattern. A single tool entry point dispatches to handlers by `action`:

```python
@mcp.tool()
async def gotify(action: GOTIFY_ACTIONS, **kwargs) -> str:
    match action:
        case "send_message":
            result = await _client.send_message(app_token=app_token, message=message, ...)
        case "list_messages":
            result = await _client.list_messages(app_id=app_id, ...)
        case _:
            return _json({"error": f"Unknown action: {action}. Call gotify_help for reference."})
    return _json(result)
```

gotify-mcp uses flat action names (no subactions). All 14 operations are top-level actions.

## Error handling

All errors return a JSON string with consistent fields:

```python
return {
    "error": "Short identifier",
    "errorCode": 401,
    "errorDescription": "Human-readable explanation.",
}
```

### HTTP error mapping

```python
try:
    response = await client.request(method, url, ...)
    response.raise_for_status()
    return response.json()
except httpx.HTTPStatusError as e:
    return {
        "error": err.get("error", f"HTTP {e.response.status_code}"),
        "errorCode": e.response.status_code,
        "errorDescription": err.get("errorDescription", "Failed to call Gotify API."),
    }
except httpx.RequestError as e:
    return {"error": "RequestError", "errorCode": 500, "errorDescription": str(e)}
```

## Health endpoint

Unauthenticated, proxies through to upstream Gotify:

```python
@mcp.custom_route("/health", methods=["GET"])
async def mcp_server_health(request):
    health = await _client.get_health()
    if "error" in health:
        return JSONResponse({"status": "error", "reason": health["error"]}, status_code=503)
    return JSONResponse({"status": "ok", "gotify": health})
```

## Bearer auth middleware

Timing-safe token validation for HTTP transport:

```python
class BearerAuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        if GOTIFY_MCP_NO_AUTH:
            return await call_next(request)
        if request.url.path in ("/health",):
            return await call_next(request)
        auth = request.headers.get("Authorization", "")
        if not auth.startswith("Bearer "):
            return JSONResponse({"error": "Unauthorized"}, status_code=401)
        if not hmac.compare_digest(auth[7:], GOTIFY_MCP_TOKEN or ""):
            return JSONResponse({"error": "Unauthorized"}, status_code=401)
        return await call_next(request)
```

## Destructive operation gate

Two-call confirmation pattern:

```python
def _destructive_gate(confirm: bool) -> str | None:
    if ALLOW_YOLO or ALLOW_DESTRUCTIVE:
        return None
    if not confirm:
        return "Destructive operation. Pass confirm=True to proceed."
    return None
```

## Upstream API client

Reusable HTTP client with per-request token selection:

```python
class GotifyClient:
    def __init__(self, base_url, client_token, timeout=20.0):
        self.base_url = normalize_service_url(base_url.rstrip("/"))
        self.client_token = client_token

    async def request(self, method, endpoint, token=None, params=None, json_data=None):
        actual_token = token if token else self.client_token
        headers = {"X-Gotify-Key": actual_token}
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.request(method, url, params=params, json=json_data, headers=headers)
```

## Docker URL rewriting

Automatic `localhost` -> `host.docker.internal` rewriting when running inside Docker:

```python
def normalize_service_url(url: str) -> str:
    if not is_docker():
        return url
    return re.sub(
        r"https?://(localhost|127\.0\.0\.1)(:\d+)?",
        lambda m: f"http://host.docker.internal{m.group(2) or ''}",
        url,
    )
```

## Environment loading

```python
from dotenv import load_dotenv
load_dotenv(dotenv_path=REPO_ROOT / ".env")

GOTIFY_URL = os.getenv("GOTIFY_URL", "")          # Required — exits if empty
GOTIFY_MCP_PORT = int(os.getenv("GOTIFY_MCP_PORT", "9158"))  # Optional with default
```

## Response truncation

```python
MAX_RESPONSE_SIZE = 512 * 1024  # 512 KB

def truncate_response(text: str) -> str:
    if len(text.encode()) > MAX_RESPONSE_SIZE:
        return text[:MAX_RESPONSE_SIZE] + "\n... [truncated]"
    return text
```

See also: [DEV](DEV.md) | [ELICITATION](ELICITATION.md) | [LOGS](LOGS.md)
