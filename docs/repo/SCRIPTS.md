# Scripts Reference — gotify-mcp

Scripts used for maintenance, hooks, and testing.

## Maintenance scripts (`scripts/`)

| Script | Purpose |
| --- | --- |
| `lint-plugin.sh` | Validate plugin manifests: required fields, version sync, schema |
| `check-docker-security.sh` | Lint Dockerfile: non-root user, no secrets, no `ADD` from URL |
| `check-no-baked-env.sh` | Verify Docker images contain no baked environment variables |
| `ensure-ignore-files.sh` | Confirm `.gitignore` and `.dockerignore` include required patterns |
| `check-outdated-deps.sh` | Report outdated dependencies (advisory, non-blocking) |
| `smoke-test.sh` | Smoke test against running server |

### Usage

```bash
# Run individually
bash scripts/lint-plugin.sh

# Run via just
just check-contract
```

## Hook scripts (`hooks/scripts/`)

Hook scripts execute automatically during Claude Code session lifecycle events.

| Script | Trigger | Purpose |
| --- | --- | --- |
| `sync-env.sh` | SessionStart | Sync `userConfig` values to `.env` with locking and backup |
| `fix-env-perms.sh` | PostToolUse | Enforce `chmod 600` on `.env` |
| `ensure-ignore-files.sh` | SessionStart | Prevent credential files from being committed |

### Environment

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

### Live test requirements

- Gotify server must be running and reachable
- `.env` must contain valid `GOTIFY_URL`, `GOTIFY_APP_TOKEN`, `GOTIFY_CLIENT_TOKEN`
- Run with: `just test-live`

## Script conventions

### Shebang and strict mode

```bash
#!/bin/bash
set -euo pipefail
```

### Variable quoting

Always quote variables:

```bash
curl -sf "$GOTIFY_URL/health"
```

### Exit codes

| Code | Meaning |
| --- | --- |
| `0` | Success / all checks pass |
| `1` | Failure / check violation |
| `2` | Usage error / missing arguments |
