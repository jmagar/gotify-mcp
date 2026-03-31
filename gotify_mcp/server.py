"""
Gotify MCP Server — two-tool design with BearerAuth middleware.

Tools:
  gotify       — all operations via action + subaction routing
  gotify_help  — returns markdown help for all actions

Transport: GOTIFY_MCP_TRANSPORT=http (default) | stdio
Auth:      GOTIFY_MCP_TOKEN (required for HTTP; skipped for stdio)
"""

from __future__ import annotations

import hmac
import json
import logging
import logging.handlers
import os
import sys
from pathlib import Path
from typing import Any, Literal

from dotenv import load_dotenv
from fastmcp import FastMCP
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from gotify_mcp.services.gotify import GotifyClient

# ---------------------------------------------------------------------------
# Environment loading
# ---------------------------------------------------------------------------
PACKAGE_DIR = Path(__file__).resolve().parent
REPO_ROOT = PACKAGE_DIR.parent
load_dotenv(dotenv_path=REPO_ROOT / ".env")

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
GOTIFY_LOG_LEVEL_STR = os.getenv(
    "GOTIFY_LOG_LEVEL", os.getenv("LOG_LEVEL", "INFO")
).upper()
NUMERIC_LOG_LEVEL = getattr(logging, GOTIFY_LOG_LEVEL_STR, logging.INFO)

logger = logging.getLogger("GotifyMCPServer")
logger.setLevel(NUMERIC_LOG_LEVEL)
logger.propagate = False

_console = logging.StreamHandler(sys.stdout)
_console.setLevel(NUMERIC_LOG_LEVEL)
_console.setFormatter(
    logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
)
if not any(isinstance(h, logging.StreamHandler) for h in logger.handlers):
    logger.addHandler(_console)

_logs_dir = REPO_ROOT / "logs"
_logs_dir.mkdir(exist_ok=True)
_file_handler = logging.handlers.RotatingFileHandler(
    _logs_dir / "gotify_mcp.log",
    maxBytes=5 * 1024 * 1024,
    backupCount=3,
    encoding="utf-8",
)
_file_handler.setLevel(NUMERIC_LOG_LEVEL)
_file_handler.setFormatter(
    logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(module)s - %(funcName)s - %(lineno)d - %(message)s"
    )
)
if not any(
    isinstance(h, logging.handlers.RotatingFileHandler) for h in logger.handlers
):
    logger.addHandler(_file_handler)

# ---------------------------------------------------------------------------
# Configuration & startup validation
# ---------------------------------------------------------------------------
GOTIFY_URL = os.getenv("GOTIFY_URL", "")
GOTIFY_CLIENT_TOKEN = os.getenv("GOTIFY_CLIENT_TOKEN")
GOTIFY_MCP_TOKEN = os.getenv("GOTIFY_MCP_TOKEN")
GOTIFY_MCP_NO_AUTH = os.getenv("GOTIFY_MCP_NO_AUTH", "").lower() in ("true", "1", "yes")
GOTIFY_MCP_TRANSPORT = os.getenv("GOTIFY_MCP_TRANSPORT", "http").lower()
GOTIFY_MCP_HOST = os.getenv("GOTIFY_MCP_HOST", "0.0.0.0")
GOTIFY_MCP_PORT = int(os.getenv("GOTIFY_MCP_PORT", "8084"))

# Destructive operations gates
ALLOW_DESTRUCTIVE = os.getenv("ALLOW_DESTRUCTIVE", "false").lower() == "true"
ALLOW_YOLO = os.getenv("ALLOW_YOLO", "false").lower() == "true"

if not GOTIFY_URL:
    print("CRITICAL: GOTIFY_URL must be set in the environment.", file=sys.stderr)
    sys.exit(1)

if GOTIFY_MCP_TRANSPORT != "stdio" and not GOTIFY_MCP_NO_AUTH and not GOTIFY_MCP_TOKEN:
    print(
        "CRITICAL: GOTIFY_MCP_TOKEN is not set.\n"
        "Set GOTIFY_MCP_TOKEN to a secure random token, or set GOTIFY_MCP_NO_AUTH=true\n"
        "to disable auth (only appropriate when secured at the network/proxy level).\n\n"
        "Generate a token with: openssl rand -hex 32",
        file=sys.stderr,
    )
    sys.exit(1)

if not GOTIFY_CLIENT_TOKEN:
    logger.warning("GOTIFY_CLIENT_TOKEN is not set. Management actions will fail.")

# ---------------------------------------------------------------------------
# Response size cap
# ---------------------------------------------------------------------------
MAX_RESPONSE_SIZE = 512 * 1024  # 512 KB


def truncate_response(text: str) -> str:
    if len(text.encode()) > MAX_RESPONSE_SIZE:
        return text[:MAX_RESPONSE_SIZE] + "\n... [truncated]"
    return text


def _json(obj: Any) -> str:
    return truncate_response(json.dumps(obj, default=str))


# ---------------------------------------------------------------------------
# Gotify API client (singleton)
# ---------------------------------------------------------------------------
_client = GotifyClient(base_url=GOTIFY_URL, client_token=GOTIFY_CLIENT_TOKEN)

# ---------------------------------------------------------------------------
# FastMCP server + BearerAuth middleware
# ---------------------------------------------------------------------------
mcp = FastMCP(
    name="Gotify MCP Server",
    instructions=(
        "Interact with Gotify push notification server. "
        "Call gotify_help to see all available actions."
    ),
)


class BearerAuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if GOTIFY_MCP_NO_AUTH:
            return await call_next(request)
        # /health is always unauthenticated
        if request.url.path in ("/health",):
            return await call_next(request)
        auth = request.headers.get("Authorization", "")
        if not auth.startswith("Bearer "):
            return JSONResponse({"error": "Unauthorized"}, status_code=401)
        provided = auth[7:]
        # Timing-safe comparison
        if not hmac.compare_digest(provided, GOTIFY_MCP_TOKEN or ""):
            return JSONResponse({"error": "Unauthorized"}, status_code=401)
        return await call_next(request)


# ---------------------------------------------------------------------------
# Destructive ops gate
# ---------------------------------------------------------------------------


def _destructive_gate(confirm: bool) -> str | None:
    """Return an error string if the destructive op should be blocked, else None."""
    if ALLOW_YOLO or ALLOW_DESTRUCTIVE:
        return None
    if not confirm:
        return "Destructive operation. Pass confirm=True to proceed."
    return None


# ---------------------------------------------------------------------------
# Tool: gotify
# ---------------------------------------------------------------------------

GOTIFY_ACTIONS = Literal[
    "send_message",
    "list_messages",
    "delete_message",
    "delete_all_messages",
    "list_applications",
    "create_application",
    "update_application",
    "delete_application",
    "list_clients",
    "create_client",
    "delete_client",
    "health",
    "version",
    "current_user",
]


@mcp.tool()
async def gotify(
    action: GOTIFY_ACTIONS,
    subaction: str = "",
    # Message params
    app_token: str = "",
    message: str = "",
    title: str = "",
    priority: int | None = None,
    message_id: int | None = None,
    extras: dict[str, Any] | None = None,
    # Application params
    app_id: int | None = None,
    name: str = "",
    description: str = "",
    default_priority: int | None = None,
    # Client params
    client_id: int | None = None,
    # Pagination / filtering
    offset: int = 0,
    limit: int = 50,
    sort_by: str = "id",
    sort_order: str = "desc",
    query: str = "",
    # Destructive gate
    confirm: bool = False,
) -> str:
    """Gotify MCP tool — routes all actions to the Gotify push notification API.

    Actions:
      send_message        — send a notification (requires app_token, message)
      list_messages       — list messages (optional: app_id, offset, limit, sort_by, sort_order, query)
      delete_message      — delete one message (requires message_id) [destructive]
      delete_all_messages — delete all messages [destructive]
      list_applications   — list apps (optional: offset, limit, query)
      create_application  — create app (requires name; optional: description, default_priority)
      update_application  — update app (requires app_id; optional: name, description, default_priority)
      delete_application  — delete app (requires app_id) [destructive]
      list_clients        — list clients (optional: offset, limit, query)
      create_client       — create client (requires name)
      delete_client       — delete client (requires client_id) [destructive]
      health              — Gotify server health check
      version             — Gotify server version
      current_user        — current authenticated user info
    """
    match action:
        case "send_message":
            if not app_token:
                return _json({"error": "app_token is required for send_message"})
            if not message:
                return _json({"error": "message is required for send_message"})
            result = await _client.send_message(
                app_token=app_token,
                message=message,
                title=title or None,
                priority=priority,
                extras=extras,
            )

        case "list_messages":
            result = await _client.list_messages(
                app_id=app_id,
                offset=offset,
                limit=limit,
                sort_by=sort_by,
                sort_order=sort_order,
                query=query,
            )

        case "delete_message":
            if (err := _destructive_gate(confirm)) is not None:
                return err
            if message_id is None:
                return _json({"error": "message_id is required for delete_message"})
            result = await _client.delete_message(message_id)

        case "delete_all_messages":
            if (err := _destructive_gate(confirm)) is not None:
                return err
            result = await _client.delete_all_messages()

        case "list_applications":
            result = await _client.list_applications(
                offset=offset, limit=limit, query=query
            )

        case "create_application":
            if not name:
                return _json({"error": "name is required for create_application"})
            result = await _client.create_application(
                name=name,
                description=description or None,
                default_priority=default_priority,
            )

        case "update_application":
            if app_id is None:
                return _json({"error": "app_id is required for update_application"})
            result = await _client.update_application(
                app_id=app_id,
                name=name or None,
                description=description or None,
                default_priority=default_priority,
            )

        case "delete_application":
            if (err := _destructive_gate(confirm)) is not None:
                return err
            if app_id is None:
                return _json({"error": "app_id is required for delete_application"})
            result = await _client.delete_application(app_id)

        case "list_clients":
            result = await _client.list_clients(offset=offset, limit=limit, query=query)

        case "create_client":
            if not name:
                return _json({"error": "name is required for create_client"})
            result = await _client.create_client(name)

        case "delete_client":
            if (err := _destructive_gate(confirm)) is not None:
                return err
            if client_id is None:
                return _json({"error": "client_id is required for delete_client"})
            result = await _client.delete_client(client_id)

        case "health":
            result = await _client.get_health()

        case "version":
            result = await _client.get_version()

        case "current_user":
            result = await _client.get_current_user()

        case _:
            return _json(
                {"error": f"Unknown action: {action}. Call gotify_help for reference."}
            )

    return _json(result)


# ---------------------------------------------------------------------------
# Tool: gotify_help
# ---------------------------------------------------------------------------

_HELP_TEXT = """# Gotify MCP Server

Interact with a Gotify push notification server.

## Tool: `gotify`

Single entry point for all operations. Use `action` to select the operation.

### Actions

| Action | Description | Required params | Destructive |
|--------|-------------|-----------------|-------------|
| `send_message` | Send a push notification | `app_token`, `message` | no |
| `list_messages` | List messages | — | no |
| `delete_message` | Delete one message | `message_id` | yes |
| `delete_all_messages` | Delete all messages | — | yes |
| `list_applications` | List applications | — | no |
| `create_application` | Create an application | `name` | no |
| `update_application` | Update an application | `app_id` | no |
| `delete_application` | Delete an application | `app_id` | yes |
| `list_clients` | List clients | — | no |
| `create_client` | Create a client | `name` | no |
| `delete_client` | Delete a client | `client_id` | yes |
| `health` | Gotify server health | — | no |
| `version` | Gotify server version | — | no |
| `current_user` | Current user info | — | no |

### Pagination parameters (list actions)

| Param | Default | Description |
|-------|---------|-------------|
| `offset` | `0` | Number of items to skip |
| `limit` | `50` | Max items to return |
| `sort_by` | `"id"` | Field to sort by |
| `sort_order` | `"desc"` | `"asc"` or `"desc"` |
| `query` | `""` | Filter by text match |

### Destructive operations

Pass `confirm=True` to execute destructive actions (delete_message, delete_all_messages,
delete_application, delete_client).

Set `ALLOW_DESTRUCTIVE=true` or `ALLOW_YOLO=true` in the server environment to skip
the confirmation gate entirely.

### Examples

```
gotify(action="send_message", app_token="AbCdEf", message="Hello", title="Test")
gotify(action="list_messages", limit=10, sort_order="desc")
gotify(action="list_messages", app_id=3, query="error")
gotify(action="delete_message", message_id=42, confirm=True)
gotify(action="list_applications")
gotify(action="create_application", name="MyApp", description="Test app")
gotify(action="health")
```
"""


@mcp.tool()
async def gotify_help() -> str:
    """Returns markdown help for all Gotify MCP actions and parameters."""
    return _HELP_TEXT


# ---------------------------------------------------------------------------
# /health endpoint (unauthenticated)
# ---------------------------------------------------------------------------


@mcp.custom_route("/health", methods=["GET"])
async def mcp_server_health(request: Request) -> JSONResponse:
    """MCP server health check."""
    if not GOTIFY_URL:
        return JSONResponse(
            {"status": "error", "reason": "GOTIFY_URL not configured."},
            status_code=500,
        )
    health = await _client.get_health()
    if "error" in health:
        return JSONResponse(
            {"status": "error", "reason": health["error"]},
            status_code=503,
        )
    return JSONResponse({"status": "ok", "gotify": health})


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main() -> None:
    logger.info(
        "Starting Gotify MCP Server — transport=%s host=%s port=%s auth=%s",
        GOTIFY_MCP_TRANSPORT,
        GOTIFY_MCP_HOST,
        GOTIFY_MCP_PORT,
        "disabled" if GOTIFY_MCP_NO_AUTH else "bearer",
    )

    if GOTIFY_MCP_TRANSPORT == "stdio":
        mcp.run(transport="stdio")
    else:
        # Add BearerAuth middleware for HTTP transport
        mcp.app.add_middleware(BearerAuthMiddleware)
        mcp.run(
            transport="streamable-http",
            host=GOTIFY_MCP_HOST,
            port=GOTIFY_MCP_PORT,
            log_level=GOTIFY_LOG_LEVEL_STR.lower(),
        )


if __name__ == "__main__":
    main()
