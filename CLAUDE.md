# gotify-mcp

MCP server for Gotify push notification management.

## Development

- Language: Python (FastMCP + uv)
- Port: 9158 (GOTIFY_MCP_PORT)
- Auth: Bearer token (GOTIFY_MCP_TOKEN)

## Commands

```bash
just dev       # run locally
just test      # run tests
just lint      # ruff check
just build     # docker build
```

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `GOTIFY_URL` | Yes | Base URL of your Gotify server |
| `GOTIFY_CLIENT_TOKEN` | Yes | Gotify client token for management |
| `GOTIFY_APP_TOKEN` | Yes | Gotify app token for sending messages |
| `GOTIFY_MCP_TOKEN` | Yes (HTTP) | Bearer token for MCP server auth |
| `GOTIFY_MCP_URL` | No | MCP server URL (for .mcp.json) |
| `GOTIFY_MCP_PORT` | No | MCP server port (default 9158) |
| `GOTIFY_MCP_HOST` | No | MCP server host (default 0.0.0.0) |
| `GOTIFY_MCP_TRANSPORT` | No | Transport mode: http or stdio (default http) |
| `GOTIFY_MCP_NO_AUTH` | No | Set true to disable bearer auth |
| `GOTIFY_LOG_LEVEL` | No | Log level (default INFO) |
| `PUID` | No | User ID for container (default 1000) |
| `PGID` | No | Group ID for container (default 1000) |

## Architecture

- `gotify_mcp/server.py` — FastMCP server entry point, action+subaction pattern
- `gotify_mcp/client.py` — Gotify HTTP API client
- `entrypoint.sh` — Container entrypoint with env validation
- `hooks/scripts/sync-env.sh` — Syncs userConfig to .env at session start
- `hooks/scripts/ensure-ignore-files.sh` — Ensures .gitignore and .dockerignore have required patterns
- `hooks/scripts/fix-env-perms.sh` — Enforces chmod 600 on .env


## Version Bumping

**Every feature branch push MUST bump the version in ALL version-bearing files.**

Bump type is determined by the commit message prefix:
- `feat!:` or `BREAKING CHANGE` → **major** (X+1.0.0)
- `feat` or `feat(...)` → **minor** (X.Y+1.0)
- Everything else (`fix`, `chore`, `refactor`, `test`, `docs`, etc.) → **patch** (X.Y.Z+1)

**Files to update (if they exist in this repo):**
- `Cargo.toml` — `version = "X.Y.Z"` in `[package]`
- `package.json` — `"version": "X.Y.Z"`
- `pyproject.toml` — `version = "X.Y.Z"` in `[project]`
- `.claude-plugin/plugin.json` — `"version": "X.Y.Z"`
- `.codex-plugin/plugin.json` — `"version": "X.Y.Z"`
- `gemini-extension.json` — `"version": "X.Y.Z"`

All files MUST have the same version. Never bump only one file.
