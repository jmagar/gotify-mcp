# Plugin Manifest Reference — gotify-mcp

Structure and conventions for plugin manifest files.

## File locations

| Platform | Path | Required |
| --- | --- | --- |
| Claude Code | `.claude-plugin/plugin.json` | yes |
| Codex | `.codex-plugin/plugin.json` | yes |
| Gemini | `gemini-extension.json` | yes |
| MCP Registry | `server.json` | yes |

All manifests must declare the same version (currently `0.3.1`). Validate with `just check-contract`.

## Claude manifest

`.claude-plugin/plugin.json`:

```json
{
  "name": "gotify-mcp",
  "version": "0.3.1",
  "description": "Gotify push notifications and management via MCP tools with HTTP fallback",
  "author": { "name": "Jacob Magar" },
  "repository": "https://github.com/jmagar/gotify-mcp",
  "license": "MIT",
  "keywords": ["gotify", "notifications", "push", "homelab", "mcp"],
  "userConfig": { ... }
}
```

### userConfig schema

| Field | Type | Title | Sensitive | Default |
| --- | --- | --- | --- | --- |
| `gotify_mcp_url` | string | Gotify MCP Server URL | no | `https://gotify.tootie.tv/mcp` |
| `gotify_mcp_token` | string | MCP Server Bearer Token | yes | — |
| `gotify_url` | string | Gotify Server URL | yes | — |
| `gotify_app_token` | string | Gotify App Token | yes | — |
| `gotify_client_token` | string | Gotify Client Token | yes | — |

## Codex manifest

`.codex-plugin/plugin.json` includes additional UI metadata:

- `interface.displayName`: "Gotify MCP"
- `interface.category`: "Utilities"
- `interface.brandColor`: "#7B44F2"
- `interface.defaultPrompt`: send alerts, list apps, review messages

## Gemini manifest

`gemini-extension.json` declares the MCP server for Gemini CLI with `uv run gotify-mcp-server` as the command and Gotify environment variables as settings.

## MCP Registry manifest

`server.json` under the `tv.tootie/gotify-mcp` namespace with PyPI package reference and stdio transport.

## Version sync

All manifests must declare identical versions. Files to update on every bump:

| File | Field |
| --- | --- |
| `pyproject.toml` | `version = "X.Y.Z"` |
| `.claude-plugin/plugin.json` | `"version": "X.Y.Z"` |
| `.codex-plugin/plugin.json` | `"version": "X.Y.Z"` |
| `gemini-extension.json` | `"version": "X.Y.Z"` |
| `CHANGELOG.md` | New entry |

Run `just check-contract` to verify all versions match.

## Cross-references

- [CONFIG.md](CONFIG.md) — userConfig and settings patterns
- [MARKETPLACES.md](MARKETPLACES.md) — Publishing and marketplace registration
