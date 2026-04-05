# Architecture Overview — gotify-mcp

## Request flow

```
MCP Client (Claude Code / Codex / Gemini)
    |
    v
Transport Layer (stdio / streamable-http)
    |
    v
BearerAuthMiddleware (timing-safe token validation)
    |
    v
Tool Router (FastMCP dispatches by tool name)
    |
    v
gotify() handler (match action: dispatch)
    |
    v
GotifyClient (httpx async client with X-Gotify-Key header)
    |
    v
Upstream Gotify Server (REST API)
```

## Module structure

```
gotify_mcp/
├── __init__.py
├── server.py                # FastMCP app, tool registration, middleware, entry point
└── services/
    └── gotify.py            # GotifyClient: async HTTP client for Gotify REST API
```

The codebase is intentionally minimal — two modules:

| Module | Responsibility |
| --- | --- |
| `server.py` | Server setup, env loading, logging, BearerAuth middleware, tool registration (`gotify` + `gotify_help`), `/health` endpoint, `main()` entry point |
| `services/gotify.py` | `GotifyClient` class: authenticated HTTP requests, message/application/client CRUD, health/version endpoints, Docker URL normalization |

## Key design decisions

### Flat action dispatch (no subactions)

gotify-mcp uses flat action names (`send_message`, `list_messages`, etc.) rather than the `action`+`subaction` pattern used by larger plugins. This is appropriate for the smaller action space (14 operations).

### Per-call app_token

The `send_message` action requires an explicit `app_token` parameter rather than reading it from the environment. This allows sending notifications from different Gotify applications without restarting the server.

### Singleton client

A single `GotifyClient` instance is created at module load time with the `GOTIFY_CLIENT_TOKEN`. This client is shared across all tool calls.

### Response as JSON string

All tool responses are serialized as JSON strings (not structured MCP content blocks). This keeps the implementation simple while providing structured data to LLM clients.

## Data flow example

```
Tool call: gotify(action="send_message", app_token="AbCdEf", message="Done", priority=7)

1. Transport receives JSON-RPC request
2. BearerAuthMiddleware validates GOTIFY_MCP_TOKEN
3. FastMCP routes to gotify() handler
4. Handler validates: app_token and message are required
5. GotifyClient.send_message() called:
   POST https://gotify.example.com/message
   X-Gotify-Key: AbCdEf
   Body: {"message": "Done", "priority": 7}
6. Upstream returns {"id": 42, "appid": 1, "message": "Done", ...}
7. Response serialized as JSON string, truncated if >512KB
8. Transport sends JSON-RPC response
```

## Error handling

| Source | Error | Response |
| --- | --- | --- |
| Auth middleware | Missing/invalid bearer token | 401 Unauthorized |
| Input validation | Missing required parameter | `{"error": "app_token is required for send_message"}` |
| Upstream client | HTTP status error | `{"error": "HTTP 404", "errorCode": 404, "errorDescription": "..."}` |
| Upstream client | Network failure | `{"error": "RequestError", "errorCode": 500, "errorDescription": "..."}` |
| Tool dispatch | Unknown action | `{"error": "Unknown action: X. Call gotify_help for reference."}` |

## Cross-references

- [TECH](TECH.md) — technology stack choices
- [TOOLS](../mcp/TOOLS.md) — MCP tool definitions
- [UPSTREAM](../upstream/CLAUDE.md) — upstream Gotify API integration
