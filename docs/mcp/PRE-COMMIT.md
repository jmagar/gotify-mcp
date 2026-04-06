# Pre-commit Hook Configuration

Hooks for `gotify-mcp` that run during Claude Code sessions and in CI.

## Hook Architecture

gotify-mcp uses Claude Code plugin hooks (defined in `hooks/hooks.json`) rather than traditional git pre-commit hooks. These run automatically during Claude Code sessions.

## hooks.json

```json
{
  "hooks": {
    "SessionStart": [
      {
        "hooks": [
          { "type": "command", "command": "${CLAUDE_PLUGIN_ROOT}/bin/sync-uv.sh", "timeout": 10 },

        ]
      }
    ],
      {
        "matcher": "Write|Edit|MultiEdit|Bash",
        "hooks": [
          { "type": "command", "command": "${CLAUDE_PLUGIN_ROOT}/bin/", "timeout": 5 }
        ]
      }
    ]
  }
}
```

## Hook Scripts

All scripts live in `bin/`. Each exits non-zero on failure.

| Script | Trigger | Purpose |
|--------|---------|---------|
The `sync-uv.sh` hook keeps the repository lockfile and persistent Python environment in sync at session start.


## CI Enforcement

The same security checks run in the `docker-security` CI job:

```bash



```

Issues caught by hooks are also caught in CI even if a developer bypasses hooks.

## CI Scripts

| Script | Purpose |
|--------|---------|
| `scripts/lint-plugin.sh` | Validates plugin manifests (schema, required fields, version sync) |





## Related Docs

- [CICD.md](CICD.md) — same checks in CI
- [DEPLOY.md](DEPLOY.md) — Dockerfile conventions enforced by hooks
- [ENV.md](ENV.md) — environment variable patterns
