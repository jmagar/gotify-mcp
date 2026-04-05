# Output Style Definitions — gotify-mcp

## Current Status

gotify-mcp does not currently define output styles. Tool responses are returned as JSON strings that LLM clients parse directly.

## Potential styles

If output styles are adopted, gotify-mcp could define:

| Style | Use case | Format |
| --- | --- | --- |
| `message-list` | `list_messages` results | Compact table with title, priority, date |
| `app-list` | `list_applications` results | Table with name, token (masked), priority |
| `notification-sent` | `send_message` confirmation | Single line: ID, app, priority |

## Cross-references

- [AGENTS.md](AGENTS.md) — Agents that would apply output styles
- [COMMANDS.md](COMMANDS.md) — Commands that would reference output styles
