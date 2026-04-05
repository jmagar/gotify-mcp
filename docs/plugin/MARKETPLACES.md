# Marketplace Publishing — gotify-mcp

Registration and publishing patterns for Claude, Codex, and Gemini marketplaces.

## Marketplace status

gotify-mcp is an **external plugin** with its own repository at `jmagar/gotify-mcp`. It is listed in the homelab-core marketplace manifest.

## Entry format

In `claude-homelab/.claude-plugin/marketplace.json`:

```json
{
  "name": "gotify-mcp",
  "source": {
    "source": "github",
    "repo": "jmagar/gotify-mcp"
  },
  "category": "utilities"
}
```

## Category

gotify-mcp is categorized as **utilities** — it provides push notification capabilities used by other plugins and workflows.

## Installation

```bash
# Via marketplace
/plugin marketplace add jmagar/gotify-mcp

# Or via homelab-core
/plugin marketplace add jmagar/claude-homelab
/plugin install gotify-mcp @jmagar-claude-homelab
```

## Version sync

On every version bump, update:

1. `pyproject.toml`, `.claude-plugin/plugin.json`, `.codex-plugin/plugin.json`, `gemini-extension.json`
2. `CHANGELOG.md` with new entry
3. The homelab-core marketplace entry (if version is tracked there)

Verify with `just check-contract`.

## Registries

| Registry | Identifier | Method |
| --- | --- | --- |
| PyPI | `gotify-mcp` | OIDC trusted publishing |
| GHCR | `ghcr.io/jmagar/gotify-mcp` | Docker multi-arch push |
| MCP Registry | `tv.tootie/gotify-mcp` | DNS auth via `tootie.tv` |

## Cross-references

- [PLUGINS.md](PLUGINS.md) — Plugin manifest structure
- [CONFIG.md](CONFIG.md) — userConfig prompted at install
- See [CHECKLIST](../CHECKLIST.md) for pre-release quality checks
