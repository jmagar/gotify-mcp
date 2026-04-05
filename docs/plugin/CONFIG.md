# Plugin Settings — gotify-mcp

Plugin configuration, user-facing settings, and environment sync.

## Configuration layers

Settings flow through three layers with clear precedence:

| Priority | Source | Managed by |
| --- | --- | --- |
| 1 (highest) | `userConfig` in plugin.json | User at install time |
| 2 | `.env` file | User or hooks |
| 3 (lowest) | System environment variables | OS/container |

## userConfig

User-facing configuration declared in `.claude-plugin/plugin.json`. Claude Code prompts the user for these values during plugin installation.

| Key | Title | Sensitive | Purpose |
| --- | --- | --- | --- |
| `gotify_mcp_url` | Gotify MCP Server URL | no | Full MCP endpoint URL |
| `gotify_mcp_token` | MCP Server Bearer Token | yes | Bearer token for MCP auth |
| `gotify_url` | Gotify Server URL | yes | Base URL of Gotify server |
| `gotify_app_token` | Gotify App Token | yes | App token for sending messages |
| `gotify_client_token` | Gotify Client Token | yes | Client token for management |

### Sensitive fields

Fields with `sensitive: true`:
- Masked in Claude Code UI
- Excluded from debug logs
- Stored securely by Claude Code
- Synced to `.env` by `sync-env.sh` hook

## Environment sync

The `sync-env.sh` hook syncs `userConfig` values to `.env` at session start:

```
userConfig (plugin.json)
  --> sync-env.sh (SessionStart hook)
    --> .env file (with file locking and backup)
      --> MCP server reads GOTIFY_URL, GOTIFY_CLIENT_TOKEN, etc.
```

### sync-env.sh behavior

1. Acquires file lock (10s timeout) to serialize concurrent sessions
2. Backs up existing `.env` (keeps 3 most recent, chmod 600)
3. Updates managed keys from `CLAUDE_PLUGIN_OPTION_*` env vars
4. Preserves keys not in userConfig
5. Validates `GOTIFY_MCP_TOKEN` is set (exits with error if not, unless `GOTIFY_MCP_NO_AUTH=true`)
6. Sets `.env` to `chmod 600`

## .env conventions

```bash
# Service credentials
GOTIFY_URL=https://gotify.example.com
GOTIFY_CLIENT_TOKEN=your_client_token
GOTIFY_APP_TOKEN=your_app_token

# MCP server
GOTIFY_MCP_PORT=9158
GOTIFY_MCP_TOKEN=generated_token_here
```

## Cross-references

- [PLUGINS.md](PLUGINS.md) — Plugin manifest where userConfig is declared
- [HOOKS.md](HOOKS.md) — Hooks that perform environment sync
- See [CONFIG](../CONFIG.md) for full environment variable reference
