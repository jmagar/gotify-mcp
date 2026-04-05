# Authentication Reference

## Overview

gotify-mcp has two authentication boundaries:

1. **Inbound** — MCP clients authenticating to the gotify-mcp server
2. **Outbound** — gotify-mcp server authenticating to the upstream Gotify instance

## Inbound Authentication (Client to MCP Server)

### Bearer Token

All HTTP requests to the MCP server require a bearer token:

```
Authorization: Bearer {GOTIFY_MCP_TOKEN}
```

The token is set via the `GOTIFY_MCP_TOKEN` environment variable. Generate one with:

```bash
openssl rand -hex 32
```

### BearerAuthMiddleware

The server validates inbound tokens using `BearerAuthMiddleware` with timing-safe comparison (`hmac.compare_digest`):

```
Request -> BearerAuthMiddleware -> Route Handler
                |
                v (401)
          Missing/invalid token
```

- Returns `401 Unauthorized` if the token is missing or does not match
- Applies to all routes except `/health`

### Unauthenticated Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/health` | GET | Health check — proxies to upstream Gotify `/health` |

The health endpoint is intentionally unauthenticated so load balancers and monitoring can probe without credentials.

### No-Auth Mode

When running behind a reverse proxy that handles authentication:

```env
GOTIFY_MCP_NO_AUTH=true
```

This disables `BearerAuthMiddleware` entirely. Only use when the proxy enforces its own auth layer (e.g., SWAG with Authelia, Cloudflare Access).

### stdio Transport

stdio transport does not use bearer tokens. Process-level isolation provides the security boundary — only the parent process (Claude Desktop, Codex CLI) can communicate with the server.

## Outbound Authentication (MCP Server to Gotify)

### Dual-Token Model

Gotify uses the `X-Gotify-Key` header with two distinct token types:

| Token | Source | Header | Used for |
| --- | --- | --- | --- |
| **App token** | Gotify UI: Settings > Apps | `X-Gotify-Key: {app_token}` | `send_message` only — passed per tool call |
| **Client token** | Gotify UI: Settings > Clients | `X-Gotify-Key: {client_token}` | All management operations |

The `GotifyClient` selects the appropriate token per request:
- `send_message` uses the explicitly provided `app_token` parameter
- All other actions use `GOTIFY_CLIENT_TOKEN` from the environment

Using the wrong token type produces a 401 from the upstream Gotify server.

### No Auth Required

Two upstream endpoints require no authentication:
- `GET /health` — server health
- `GET /version` — server version

## Plugin userConfig Integration

When installed as a Claude Code plugin, credentials are managed via `userConfig` in `plugin.json`:

```json
{
  "userConfig": {
    "gotify_mcp_url": { "sensitive": false },
    "gotify_mcp_token": { "sensitive": true },
    "gotify_url": { "sensitive": true },
    "gotify_app_token": { "sensitive": true },
    "gotify_client_token": { "sensitive": true }
  }
}
```

Fields marked `sensitive: true` are stored encrypted and synced to `.env` by the `sync-env.sh` hook at session start.

## Security Best Practices

- Never log tokens — not even at DEBUG level
- Rotate credentials regularly — update `.env` and restart the server
- Use HTTPS in production for `GOTIFY_URL`
- Restrict token scope — use app tokens for sending, client tokens for management
- Generate dedicated tokens for the MCP server rather than reusing personal tokens

## See Also

- [ENV.md](ENV.md) — Full environment variable reference
- [TRANSPORT.md](TRANSPORT.md) — Transport-specific auth behavior
