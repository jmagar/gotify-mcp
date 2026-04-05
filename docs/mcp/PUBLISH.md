# Publishing Strategy

Versioning and release workflow for `gotify-mcp`.

## Versioning

Semantic versioning (MAJOR.MINOR.PATCH). Bump type from commit prefix:

| Prefix | Bump | Example |
|--------|------|---------|
| `feat!:` / `BREAKING CHANGE` | Major | `0.3.1` -> `1.0.0` |
| `feat:` / `feat(scope):` | Minor | `0.3.1` -> `0.4.0` |
| `fix:`, `docs:`, `chore:`, etc. | Patch | `0.3.1` -> `0.3.2` |

## Version Sync

All version-bearing files MUST match. Update together:

| File | Field |
|------|-------|
| `pyproject.toml` | `version = "X.Y.Z"` in `[project]` |
| `.claude-plugin/plugin.json` | `"version": "X.Y.Z"` |
| `.codex-plugin/plugin.json` | `"version": "X.Y.Z"` |
| `gemini-extension.json` | `"version": "X.Y.Z"` |
| `server.json` | `"version": "X.Y.Z"` (updated by publish workflow) |
| `CHANGELOG.md` | New entry under `## X.Y.Z` |

## Publish Workflow

```bash
just publish [major|minor|patch]
```

Steps executed:

1. Verify on `main` branch with clean working tree
2. Pull latest from origin
3. Bump version in `pyproject.toml`, `.claude-plugin/plugin.json`, `.codex-plugin/plugin.json`, `gemini-extension.json`
4. Commit: `release: vX.Y.Z`
5. Tag: `vX.Y.Z`
6. Push to origin (triggers CI/CD publish workflows)

## Package Registries

| Registry | Method | Identifier |
|----------|--------|------------|
| PyPI | Trusted publishing via OIDC | `gotify-mcp` |
| GHCR | Multi-arch Docker images | `ghcr.io/jmagar/gotify-mcp` |
| MCP Registry | DNS auth via `tootie.tv` | `tv.tootie/gotify-mcp` |

## server.json

MCP Registry metadata file at repo root:

```json
{
  "name": "tv.tootie/gotify-mcp",
  "title": "Gotify MCP",
  "description": "MCP server for self-hosted Gotify push notifications and message management.",
  "version": "0.3.1",
  "packages": [
    {
      "registryType": "pypi",
      "identifier": "gotify-mcp",
      "runtimeHint": "uvx",
      "transport": { "type": "stdio" }
    }
  ]
}
```

## Verification

After publishing, verify:

```bash
# PyPI
pip install gotify-mcp==X.Y.Z

# Docker
docker pull ghcr.io/jmagar/gotify-mcp:vX.Y.Z

# GitHub Release
gh release view vX.Y.Z
```

## Related Docs

- [CICD.md](CICD.md) — publish workflows triggered by tags
- [DEPLOY.md](DEPLOY.md) — package manager install commands
