# Channel Integration — gotify-mcp

## Current Status

gotify-mcp does not currently implement channel integration. Gotify itself is a notification channel — it sends push notifications to mobile and desktop clients via the Gotify app.

## Gotify as a notification sink

The gotify skill is designed to be a notification sink for other Claude Code workflows:

| Trigger | Notification |
| --- | --- |
| Long-running task completes | Push with task summary and status |
| Plan implementation finishes | Push with completion details |
| Blocked — need user input | Push with question and context |
| Task transition | Push with review request |

## Integration with other channels

gotify-mcp could complement Discord or Telegram channels:

- Send Gotify notifications for mobile push alerts
- Use Discord for interactive conversations
- Use Gotify for fire-and-forget status updates

## Cross-references

- [HOOKS.md](HOOKS.md) — Hooks that may trigger notifications
- [SKILLS.md](SKILLS.md) — Skill auto-invocation rules
