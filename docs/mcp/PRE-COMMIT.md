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
          { "type": "command", "command": "${CLAUDE_PLUGIN_ROOT}/hooks/scripts/sync-env.sh", "timeout": 10 },
          { "type": "command", "command": "${CLAUDE_PLUGIN_ROOT}/hooks/scripts/ensure-ignore-files.sh", "timeout": 5 }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Write|Edit|MultiEdit|Bash",
        "hooks": [
          { "type": "command", "command": "${CLAUDE_PLUGIN_ROOT}/hooks/scripts/fix-env-perms.sh", "timeout": 5 }
        ]
      }
    ]
  }
}
```

## Hook Scripts

All scripts live in `hooks/scripts/`. Each exits non-zero on failure.

| Script | Trigger | Purpose |
|--------|---------|---------|
| `sync-env.sh` | SessionStart | Syncs `userConfig` credentials to `.env` with file locking and backup |
| `ensure-ignore-files.sh` | SessionStart | Verifies `.gitignore` and `.dockerignore` contain required patterns |
| `fix-env-perms.sh` | PostToolUse | Sets `.env` to `chmod 600` after any file write or shell command |

## CI Enforcement

The same security checks run in the `docker-security` CI job:

```bash
bash scripts/check-docker-security.sh Dockerfile
bash scripts/check-no-baked-env.sh .
bash scripts/ensure-ignore-files.sh --check .
```

Issues caught by hooks are also caught in CI even if a developer bypasses hooks.

## CI Scripts

| Script | Purpose |
|--------|---------|
| `scripts/lint-plugin.sh` | Validates plugin manifests (schema, required fields, version sync) |
| `scripts/check-docker-security.sh` | Lints Dockerfile: non-root user, no secrets |
| `scripts/check-no-baked-env.sh` | Ensures no `ENV` directives contain secrets |
| `scripts/ensure-ignore-files.sh` | Verifies `.env` appears in ignore files |
| `scripts/check-outdated-deps.sh` | Warns on outdated dependencies (advisory) |

## Related Docs

- [CICD.md](CICD.md) — same checks in CI
- [DEPLOY.md](DEPLOY.md) — Dockerfile conventions enforced by hooks
- [ENV.md](ENV.md) — environment variable patterns
