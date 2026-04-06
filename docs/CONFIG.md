# Configuration Reference — gotify-mcp

Complete environment variable reference and configuration options.

## Deployment paths

| Path | Transport | Credentials source | Auth |
|------|-----------|-------------------|------|
| **Plugin (stdio)** | stdio | `userConfig` in plugin.json, interpolated via `.mcp.json` | None |
| **Docker (HTTP)** | http | `.env` file | Bearer token (`GOTIFY_MCP_TOKEN`) |

### Plugin quickstart

Install the plugin in Claude Code. You will be prompted for:
- **Gotify Server URL** — base URL of your Gotify server
- **Gotify App Token** — for sending messages
- **Gotify Client Token** — for management operations

No `.env` file needed. See [plugin/CONFIG.md](plugin/CONFIG.md) for details.

### Docker quickstart

```bash
cp .env.example .env
chmod 600 .env
# Edit .env with your credentials
docker compose up -d
```

## Environment variables

### Gotify server credentials

| Variable | Required | Default | Sensitive | Description |
| --- | --- | --- | --- | --- |
| `GOTIFY_URL` | yes | — | no | Base URL of your Gotify server (no trailing slash). Server exits if unset. |
| `GOTIFY_CLIENT_TOKEN` | yes* | — | yes | Client token for management operations (list messages, manage apps/clients). Found in Gotify UI under Settings > Clients. |
| `GOTIFY_APP_TOKEN` | no | — | yes | App token for sending messages via HTTP fallback. The MCP tool requires `app_token` per call. |

*Without `GOTIFY_CLIENT_TOKEN`, all management actions return 401. A warning is logged at startup.

### MCP server

| Variable | Required | Default | Sensitive | Description |
| --- | --- | --- | --- | --- |
| `GOTIFY_MCP_HOST` | no | `0.0.0.0` | no | Network interface to bind |
| `GOTIFY_MCP_PORT` | no | `9158` | no | HTTP server port |
| `GOTIFY_MCP_TOKEN` | yes** | — | yes | Bearer token for HTTP auth. Generate: `openssl rand -hex 32` |
| `GOTIFY_MCP_TRANSPORT` | no | `http` | no | Transport mode: `http` or `stdio` |
| `GOTIFY_MCP_NO_AUTH` | no | `false` | no | Disable bearer auth (only behind trusted proxy) |

**Required when transport is `http` and `GOTIFY_MCP_NO_AUTH` is not `true`. Server exits if neither is set.

### Logging

| Variable | Required | Default | Sensitive | Description |
| --- | --- | --- | --- | --- |
| `GOTIFY_LOG_LEVEL` | no | `INFO` | no | `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL` |

Logs are written to `logs/gotify_mcp.log` with rotation (5 MB max, 3 backups).

### Safety

| Variable | Required | Default | Sensitive | Description |
| --- | --- | --- | --- | --- |
| `ALLOW_DESTRUCTIVE` | no | `false` | no | Skip `confirm=True` for destructive actions |
| `ALLOW_YOLO` | no | `false` | no | Alias for `ALLOW_DESTRUCTIVE` |

### Docker / container

| Variable | Required | Default | Sensitive | Description |
| --- | --- | --- | --- | --- |
| `PUID` | no | `1000` | no | UID for container process |
| `PGID` | no | `1000` | no | GID for container process |
| `DOCKER_NETWORK` | no | — | no | External Docker network name |

## Gotify dual-token model

Gotify uses two separate token types. Using the wrong token type produces a 401 error.

| Token | Where to create | Used for |
| --- | --- | --- |
| **App token** | Gotify UI: Settings > Apps > Create Application | Sending messages only. Passed per call as `app_token`. |
| **Client token** | Gotify UI: Settings > Clients > Create Client | All management operations: list/delete messages, manage apps and clients, current user. |

The MCP server reads `GOTIFY_CLIENT_TOKEN` from the environment for management actions. The `app_token` for `send_message` is always passed explicitly per tool call.

## .env.example conventions

- Group variables by section with comment headers
- Required variables first within each group
- No actual secrets — use descriptive placeholders
- Include usage instructions at the bottom

See [ENV](mcp/ENV.md) for the transport-specific variable details.
