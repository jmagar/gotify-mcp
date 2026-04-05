# Hook Configuration — gotify-mcp

Lifecycle hooks that run automatically during Claude Code sessions.

## File location

```
hooks/
  hooks.json                   # Hook declarations
  scripts/
    sync-env.sh                # Sync userConfig to .env
    fix-env-perms.sh           # Enforce chmod 600 on .env
    ensure-ignore-files.sh     # Keep .gitignore aligned
```

## hooks.json structure

```json
{
  "description": "Sync credentials and enforce security",
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

## Hook events

| Event | When it fires | Purpose in gotify-mcp |
| --- | --- | --- |
| `SessionStart` | Claude Code session begins | Sync credentials from userConfig to `.env`, validate ignore files |
| `PostToolUse` | After Write/Edit/Bash | Enforce `chmod 600` on `.env` |

## Hook scripts

### sync-env.sh

Syncs `userConfig` values into `.env` with concurrency safety:

- Acquires a file lock (`flock -w 10`) to prevent race conditions between concurrent sessions
- Maps `CLAUDE_PLUGIN_OPTION_*` environment variables to `.env` keys
- Backs up `.env` before writing (keeps 3 most recent backups, all `chmod 600`)
- Uses `awk` for safe value replacement (no delimiter injection)
- Validates `GOTIFY_MCP_TOKEN` is set (fails with actionable error if not)
- Skips validation when `GOTIFY_MCP_NO_AUTH=true`

### fix-env-perms.sh

Enforces restrictive permissions on `.env` after any file operation:

```bash
if [[ -f "$ENV_FILE" ]]; then
  chmod 600 "$ENV_FILE"
fi
```

### ensure-ignore-files.sh

Verifies `.gitignore` and `.dockerignore` contain patterns that prevent credential leaks.

## Path variables

| Variable | Expands to |
| --- | --- |
| `${CLAUDE_PLUGIN_ROOT}` | Absolute path to the gotify-mcp plugin directory |

## Cross-references

- [CONFIG.md](CONFIG.md) — Settings that hooks sync
- [PLUGINS.md](PLUGINS.md) — Plugin manifest where hooks are registered
- See [GUARDRAILS](../GUARDRAILS.md) for security patterns enforced by hooks
