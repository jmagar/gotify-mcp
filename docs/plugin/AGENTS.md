# Agent Definitions — gotify-mcp

## Current Status

gotify-mcp does not currently define any agents. All functionality is exposed through the `gotify` and `gotify_help` MCP tools, accessed via the `skills/gotify/SKILL.md` skill definition.

## When agents would be useful

Agents could be added if gotify-mcp gains:

- Complex multi-step notification workflows (e.g., a notification orchestrator)
- Monitoring workflows that combine Gotify with other services
- Automated alert triage and response

## Agent patterns

If an agent is added, it would follow this structure:

```
agents/
  gotify-specialist.md
```

With frontmatter:

```yaml
---
name: gotify-specialist
description: |
  Use this agent when the user asks about notification management,
  Gotify configuration, or push alert troubleshooting.
tools:
  - Bash
  - Read
  - mcp__gotify-mcp__gotify
  - mcp__gotify-mcp__gotify_help
---
```

## Cross-references

- [SKILLS.md](SKILLS.md) — Current skill-based approach
- [COMMANDS.md](COMMANDS.md) — Commands that may invoke agents
