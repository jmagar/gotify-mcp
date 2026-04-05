# Web MCP Integration

Browser-accessible MCP endpoints for web dashboards and admin panels.

## What is Web MCP

Web MCP exposes MCP server capabilities over HTTP with browser-compatible configuration. The server's HTTP transport (`http://localhost:9158/mcp`) is the foundation.

## Use Cases

| Use case | Description |
|----------|-------------|
| Notification dashboard | Web UI that lists messages, sends test notifications |
| Admin panel | Manage Gotify applications and clients via browser |
| Monitoring | Browser-based health and version checks |

## Implementation Status

gotify-mcp uses streamable-HTTP transport by default, which is accessible from browser clients via standard `fetch()` calls.

### CORS

gotify-mcp does not currently configure CORS middleware. To enable browser access from a different origin, CORS headers would need to be added:

```python
from starlette.middleware.cors import CORSMiddleware

mcp.app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://dashboard.example.com"],
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)
```

### Health Endpoint

The `/health` endpoint is already browser-accessible (no auth, no CORS issues for same-origin):

```bash
curl -s http://localhost:9158/health
```

## Security Considerations

- Bearer tokens in browser contexts must be stored securely (not in `localStorage`)
- Consider session cookies with `HttpOnly`, `Secure`, `SameSite=Strict` for web clients
- Rate limiting may be needed for browser-originated requests
- Read-only tokens for dashboard views vs read-write for admin actions

## Future Direction

- CORS middleware configuration via environment variable
- Session-based auth as alternative to bearer tokens for browsers
- Integration with MCP UI for rich tool forms (see [MCPUI](MCPUI.md))

See also: [AUTH](AUTH.md) | [TRANSPORT](TRANSPORT.md) | [MCPUI](MCPUI.md)
