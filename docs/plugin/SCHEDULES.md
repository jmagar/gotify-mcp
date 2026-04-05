# Scheduled Tasks — gotify-mcp

## Current Status

gotify-mcp does not currently define scheduled tasks. However, the notification skill is designed to be invoked automatically by other workflows.

## Potential schedules

| Schedule | Cron | Purpose |
| --- | --- | --- |
| Health check | `*/5 * * * *` | Verify Gotify server is responsive |
| Message digest | `0 */6 * * *` | Summarize unread messages |
| App token audit | `0 0 * * 1` | List applications and check for unused tokens |

## Example: scheduled health check

```json
{
  "name": "gotify-health",
  "schedule": "*/5 * * * *",
  "prompt": "Check Gotify health. If DOWN, report the error. If OK, do nothing.",
  "enabled": true
}
```

## Cross-references

- [AGENTS.md](AGENTS.md) — Agents invoked by schedules
- [CHANNELS.md](CHANNELS.md) — Notification patterns for schedule alerts
