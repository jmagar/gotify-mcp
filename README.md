# Gotify MCP

MCP server for self-hosted Gotify. This repo exposes a unified `gotify` action router and a `gotify_help` companion tool for sending notifications and managing Gotify messages, applications, clients, and account metadata.

## What this repository ships

- `gotify_mcp/`: FastMCP server and Gotify API service client
- `skills/gotify/`: client-facing skill docs
- `docs/gotify-api.json`: bundled upstream API reference
- `.claude-plugin/`, `.codex-plugin/`, `gemini-extension.json`: client manifests
- `docker-compose.yml`, `Dockerfile`, `entrypoint.sh`: container deployment
- `scripts/`: smoke tests and contract checks

## MCP surface

### Main tools

| Tool | Purpose |
| --- | --- |
| `gotify` | Unified action router for notifications, apps, clients, and health |
| `gotify_help` | Markdown help for actions and parameters |

### Supported actions

| Action | Purpose |
| --- | --- |
| `send_message` | Send a push notification using an app token |
| `list_messages` | List messages |
| `delete_message` | Delete one message |
| `delete_all_messages` | Delete all messages |
| `list_applications` | List apps |
| `create_application` | Create an app |
| `update_application` | Update an app |
| `delete_application` | Delete an app |
| `list_clients` | List clients |
| `create_client` | Create a client |
| `delete_client` | Delete a client |
| `health` | Check server health |
| `version` | Get Gotify version |
| `current_user` | Get current authenticated user |

Destructive actions are gated by `confirm=true` unless the server is configured to allow them automatically.

## Installation

### Marketplace

```bash
/plugin marketplace add jmagar/claude-homelab
/plugin install gotify-mcp @jmagar-claude-homelab
```

### Local development

```bash
uv sync --dev
uv run gotify-mcp-server
```

Equivalent direct module run:

```bash
uv run python -m gotify_mcp.server
```

## Configuration

Create `.env` from `.env.example` and set:

```bash
GOTIFY_URL=https://your-gotify-instance.example.com
GOTIFY_CLIENT_TOKEN=your_gotify_client_token
GOTIFY_APP_TOKEN=your_gotify_app_token
GOTIFY_MCP_HOST=0.0.0.0
GOTIFY_MCP_PORT=9158
GOTIFY_MCP_TRANSPORT=http
GOTIFY_MCP_TOKEN=...
GOTIFY_MCP_NO_AUTH=false
GOTIFY_LOG_LEVEL=INFO
```

Notes:

- `GOTIFY_URL` is required or the server exits at startup.
- `GOTIFY_CLIENT_TOKEN` is required for management actions.
- `GOTIFY_APP_TOKEN` is used when sending notifications.
- `GOTIFY_MCP_TRANSPORT` supports `http` and `stdio`.

## Typical operations

```text
gotify action=send_message app_token=... message="Build finished" priority=5
gotify action=list_messages limit=20
gotify action=list_applications
gotify action=current_user
gotify_help
```

## Development commands

```bash
just dev
just lint
just fmt
just typecheck
just test
just up
just logs
just health
```

## Verification

Recommended:

```bash
just lint
just typecheck
just test
```

Optional live verification:

```bash
just test-live
```

## Related files

- `gotify_mcp/server.py`: MCP server and action router
- `gotify_mcp/services/`: Gotify API client logic
- `docs/gotify-api.json`: upstream reference snapshot
- `skills/gotify/`: client guidance

## License

MIT
