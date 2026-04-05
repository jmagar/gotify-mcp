# Slash Commands — gotify-mcp

## Current Status

gotify-mcp does not currently define slash commands. The `gotify` skill is invoked automatically based on trigger phrases in the SKILL.md description, and MCP tools are called directly.

## When commands would be useful

Commands could be added for frequent operations:

| Potential command | Purpose |
| --- | --- |
| `/gotify:send` | Send a notification with prompted arguments |
| `/gotify:status` | Check Gotify server health and list recent messages |
| `/gotify:apps` | List all applications with their tokens |

## Command patterns

If commands are added, they would live in:

```
commands/
  gotify/
    send.md          # /gotify:send
    status.md        # /gotify:status
```

Example command file:

```markdown
---
description: Send a Gotify push notification
argument-hint: <message> [--priority N]
allowed-tools: mcp__gotify-mcp__gotify
---

Send a Gotify notification: $ARGUMENTS

## Instructions
1. Parse the message and optional priority from arguments
2. Retrieve the app token from the environment
3. Call gotify(action="send_message", ...) with the provided parameters
4. Report success with the message ID
```

## Cross-references

- [SKILLS.md](SKILLS.md) — Skill that provides domain knowledge
- [AGENTS.md](AGENTS.md) — Agents that commands may delegate to
