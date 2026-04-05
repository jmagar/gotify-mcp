# Skill Definitions — gotify-mcp

The gotify skill definition and its patterns.

## Directory structure

```
skills/
  gotify/
    SKILL.md                  # Skill definition
```

## SKILL.md frontmatter

```yaml
---
name: gotify
description: This skill should be used when the user asks to "send notification",
  "notify me when done", "push notification", "alert me", "Gotify notification",
  or mentions push notifications, task alerts, or Gotify. Also automatically
  invoked for long-running tasks >5 minutes, plan completion, user input required,
  or task transitions.
---
```

## Key features of the gotify skill

### Mandatory auto-invocation

The gotify skill is unique in that it MUST be invoked automatically (without user request) for:

1. Long-running tasks estimated to take >5 minutes
2. Plan completion milestones
3. Blocked states requiring user input
4. Task transitions needing review/approval

### Dual mode: MCP and HTTP fallback

The skill documents both MCP tool calls and direct HTTP fallback via `curl`:

- **MCP mode** (preferred): `gotify(action="send_message", ...)`
- **HTTP fallback**: `curl -X POST "$GOTIFY_URL/message" -H "X-Gotify-Key: $GOTIFY_APP_TOKEN"`

### Notification format requirements

All notifications must include:
- Project/working directory (`basename` of cwd)
- Task description
- Session ID (`session-YYYY-MM-DD-HH-MM`)
- Status/next action

### Priority reference

| Range | Level | Use |
|-------|-------|-----|
| 0-3 | Low | Info, FYI |
| 4-7 | Normal | Task updates, completions |
| 8-10 | High | Blocked, errors, urgent |

## Token retrieval pattern

The `app_token` for `send_message` is not read from the server environment. It must be retrieved from the plugin's userConfig:

```bash
echo "$CLAUDE_PLUGIN_OPTION_GOTIFY_APP_TOKEN"
```

## Cross-references

- [AGENTS.md](AGENTS.md) — Agents that might delegate to this skill
- [COMMANDS.md](COMMANDS.md) — Slash commands that may reference the skill
- See [INVENTORY](../INVENTORY.md) for the complete component list
