# Scripts Reference — gotify-mcp

Scripts used for maintenance, hooks, and testing.

## Maintenance scripts (`scripts/`)

| Script | Purpose |
| --- | --- |
| `lint-plugin.sh` | Validate plugin manifests: required fields, version sync, schema |




| `smoke-test.sh` | Smoke test against running server |

Usage

```bash
# Run individually
bash scripts/lint-plugin.sh

# Run via just
just check-contract
```

## Hook scripts (`bin/`)

Hook scripts execute automatically during Claude Code session lifecycle events.

| Script | Trigger | Purpose |
| --- | --- | --- |
The `sync-uv.sh` hook keeps the repository lockfile and persistent Python environment in sync at session start.


Environment

Hook scripts receive `$CLAUDE_PLUGIN_ROOT` pointing to the plugin installation directory:

```bash
#!/bin/bash
set -euo pipefail
ENV_FILE="$CLAUDE_PLUGIN_ROOT/.env"
```

## Test scripts (`tests/`)

| Script | Purpose |
| --- | --- |
| `test_live.sh` | Live integration test suite against running Gotify server |

Live test requirements

- Gotify server must be running and reachable
- `.env` must contain valid `GOTIFY_URL`, `GOTIFY_APP_TOKEN`, `GOTIFY_CLIENT_TOKEN`
- Run with: `just test-live`

## Script conventions

Shebang and strict mode

```bash
#!/bin/bash
set -euo pipefail
```

Variable quoting

Always quote variables:

```bash
curl -sf "$GOTIFY_URL/health"
```

Exit codes

| Code | Meaning |
| --- | --- |
| `0` | Success / all checks pass |
| `1` | Failure / check violation |
| `2` | Usage error / missing arguments |
