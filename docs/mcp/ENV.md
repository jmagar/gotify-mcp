# Environment Variable Reference

## Deployment paths

gotify-mcp supports two deployment models:

| Path | Transport | Credentials | Auth |
|------|-----------|-------------|------|
| **Plugin (stdio)** | stdio | `${userConfig.*}` in `.mcp.json` | None (stdio) |
| **Docker (HTTP)** | http | `.env` file | Bearer token |

For plugin deployment, sensitive vars are interpolated from `userConfig` — see [Plugin CONFIG](../plugin/CONFIG.md).

## Upstream Service

| Variable | Required | Default | Description | Sensitive |
|----------|----------|---------|-------------|-----------|
| `GOTIFY_URL` | yes | — | Base URL of the Gotify server (no trailing slash) | no |
| `GOTIFY_CLIENT_TOKEN` | yes* | — | Client token for management operations | **yes** |
| `GOTIFY_APP_TOKEN` | no | — | App token for HTTP fallback sending (MCP tool uses per-call `app_token`) | **yes** |

*Without `GOTIFY_CLIENT_TOKEN`, management actions fail with 401. A warning is logged at startup.

## MCP Server

| Variable | Required | Default | Description | Sensitive |
|----------|----------|---------|-------------|-----------|
| `GOTIFY_MCP_HOST` | no | `0.0.0.0` | Bind address for HTTP transport | no |
| `GOTIFY_MCP_PORT` | no | `9158` | Listen port for HTTP transport | no |
| `GOTIFY_MCP_TOKEN` | yes** | — | Bearer token for inbound MCP auth | **yes** |
| `GOTIFY_MCP_TRANSPORT` | no | `http` | Transport mode: `http` or `stdio` | no |
| `GOTIFY_MCP_NO_AUTH` | no | `false` | Disable inbound auth (use behind reverse proxy only) | no |

**Not required when `GOTIFY_MCP_NO_AUTH=true` or when using `stdio` transport.

## Logging

| Variable | Required | Default | Description | Sensitive |
|----------|----------|---------|-------------|-----------|
| `GOTIFY_LOG_LEVEL` | no | `INFO` | Log verbosity: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL` | no |

Logs are written to `logs/gotify_mcp.log` with rotating file handler (5 MB max, 3 backups).

## Safety Gates

| Variable | Required | Default | Description | Sensitive |
|----------|----------|---------|-------------|-----------|
| `ALLOW_DESTRUCTIVE` | no | `false` | Auto-confirm destructive operations | no |
| `ALLOW_YOLO` | no | `false` | Alias for `ALLOW_DESTRUCTIVE` | no |

## Docker / Runtime

| Variable | Required | Default | Description | Sensitive |
|----------|----------|---------|-------------|-----------|
| `PUID` | no | `1000` | Container user ID | no |
| `PGID` | no | `1000` | Container group ID | no |
| `DOCKER_NETWORK` | no | — | Docker network to join | no |
| `PYTHONUNBUFFERED` | no | `1` | Disable Python output buffering (set in Dockerfile) | no |

## Token Generation

Generate a secure MCP token (Docker/HTTP deployment only):

```bash
openssl rand -hex 32
```

Store the result in `GOTIFY_MCP_TOKEN` in your `.env` file.

## See Also

- [AUTH.md](AUTH.md) — How tokens are used for authentication
- [TRANSPORT.md](TRANSPORT.md) — Transport-specific variable usage
- [../plugin/CONFIG.md](../plugin/CONFIG.md) — Plugin userConfig fields
