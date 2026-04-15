# Plugin Settings — gotify-mcp

Plugin configuration and user-facing settings for Claude Code plugin deployment.

## How it works

When installed as a Claude Code plugin, credentials flow through two files:

1. **`plugin.json`** — declares `userConfig` fields that Claude Code prompts for at install time
2. **`.mcp.json`** — references those fields as `${userConfig.<key>}` in the `env` section

```
plugin.json userConfig (user enters values)
  --> .mcp.json env (${userConfig.*} interpolated by Claude Code)
    --> MCP server reads GOTIFY_URL, GOTIFY_CLIENT_TOKEN, etc.
```

No `.env` file or sync script is needed for plugin deployment. Claude Code handles interpolation directly.

## userConfig fields

| Key | Title | Sensitive | Purpose |
| --- | --- | --- | --- |
| `gotify_url` | Gotify Server URL | yes | Base URL of Gotify server |
| `gotify_app_token` | Gotify App Token | yes | App token for sending messages |
| `gotify_client_token` | Gotify Client Token | yes | Client token for management |

Sensitive fields are masked in the Claude Code UI, excluded from debug logs, and stored securely.

## Defaults hardcoded in .mcp.json

These values are set directly in `.mcp.json` and not exposed in userConfig:

| Variable | Value | Why |
| --- | --- | --- |
| `GOTIFY_MCP_TRANSPORT` | `stdio` | Plugin always uses stdio |
| `GOTIFY_MCP_NO_AUTH` | `true` | No HTTP auth needed for stdio |
| `GOTIFY_LOG_LEVEL` | `INFO` | Sensible default |
| `ALLOW_DESTRUCTIVE` | `false` | Safety gate |

## SessionStart hook

The `sync-uv.sh` hook runs on session start to ensure Python dependencies are installed:

```
hooks/hooks.json → bin/sync-uv.sh
  --> uv sync --project ${CLAUDE_PLUGIN_ROOT}
  --> venv at ${CLAUDE_PLUGIN_DATA}/.venv
```

This prevents cold-start delays from uv needing to build wheels on first tool call.

## Docker deployment

For Docker Compose deployment, use `.env` file instead. See [CONFIG](../CONFIG.md) for full variable reference.

## Cross-references

- [HOOKS.md](HOOKS.md) — Hook definitions
- [CONFIG](../CONFIG.md) — Full environment variable reference
- [ENV](../mcp/ENV.md) — Transport-specific variable details
