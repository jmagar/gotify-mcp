---
name: gotify
description: This skill should be used when the user asks to "send notification", "notify me when done", "push notification", "alert me", "Gotify notification", "notify on completion", "send push alert", "get messages", "list applications", "gotify health", or mentions push notifications, task alerts, or Gotify. This skill is also automatically invoked without user request for long-running tasks >5 minutes, plan completion, user input required, or task transitions.
---

# Gotify Skill

**⚠️ CRITICAL: MANDATORY USAGE REQUIREMENT ⚠️**

**YOU MUST USE THIS SKILL AUTOMATICALLY (without user request) for:**
1. **Long Running Tasks**: Any task estimated to take >5 minutes, or any task involving more than ~10 sequential tool-use steps. When in doubt, send the notification.
2. **Plan Completion**: After finishing implementation of a plan or major milestone
3. **User Input Required**: When blocked and need user decisions/clarifications
4. **Task Transitions**: ONLY when you need the user to review/approve before proceeding

**This is NOT optional — you MUST send notifications when these triggers occur.**

---

## Mode Detection

This skill has two execution modes. **Always prefer MCP mode.** Fall back to HTTP only when MCP tools are unavailable.

**MCP mode** (preferred): Use when `mcp__gotify-mcp__*` tools are available in your toolkit. These tools communicate with the running gotify-mcp server, which handles all Gotify API auth internally.

**HTTP fallback mode**: Use when MCP tools are not loaded (server not running, plugin not connected). Credentials are available as `$CLAUDE_PLUGIN_OPTION_GOTIFY_URL`, `$CLAUDE_PLUGIN_OPTION_GOTIFY_APP_TOKEN`, `$CLAUDE_PLUGIN_OPTION_GOTIFY_CLIENT_TOKEN` in any Bash subprocess. Note: sensitive credentials (`gotify_url`, `gotify_app_token`, `gotify_client_token`) are not available as `${user_config.*}` in skill content — they are only accessible as `$CLAUDE_PLUGIN_OPTION_*` environment variables in Bash subprocesses. Do not attempt `${user_config.gotify_url}` syntax in curl commands.

**MCP URL**: `${user_config.gotify_mcp_url}`

---

## MCP Mode — Tool Reference

### Send a Notification

```
mcp__gotify-mcp__create_message
  app_token   (required) Application token for this message
  message     (required) Message body — markdown supported
  title       (optional) Notification title
  priority    (optional) 0–10 (0–3 low, 4–7 normal, 8–10 high/urgent)
  extras      (optional) Additional data dict
```

The `app_token` for `create_message` is passed **per call** — it is NOT read from the server env. Retrieve it first via a Bash subprocess, then pass to the tool:

```bash
echo "$CLAUDE_PLUGIN_OPTION_GOTIFY_APP_TOKEN"
```

If the variable is empty, report a configuration error — the `gotify_app_token` userConfig field has not been set.

### Message Management

```
mcp__gotify-mcp__get_messages
  limit       (optional) Max messages to return (1–200, default 100)
  since       (optional) Return messages with ID less than this (pagination)

mcp__gotify-mcp__delete_message
  message_id  (required) Integer ID of message to delete

mcp__gotify-mcp__delete_all_messages
  (no parameters — deletes all messages across all applications)
```

### Application Management

```
mcp__gotify-mcp__get_applications
  (no parameters)

mcp__gotify-mcp__create_application
  name              (required) Application name
  description       (optional) Description
  default_priority  (optional) Default message priority

mcp__gotify-mcp__update_application
  app_id            (required) Integer application ID
  name              (optional) New name
  description       (optional) New description
  default_priority  (optional) New default priority

mcp__gotify-mcp__delete_application
  app_id            (required) Integer application ID
```

### Client Management

```
mcp__gotify-mcp__get_clients
  (no parameters)

mcp__gotify-mcp__create_client
  name  (required) Client name
```

### Server Info

```
mcp__gotify-mcp__get_health
  (no parameters — no auth required)

mcp__gotify-mcp__get_version
  (no parameters — no auth required)
```

### Resources

```
gotify://application/{app_id}/messages   — messages for a specific app
gotify://currentuser                     — current authenticated user info
```

---

## HTTP Fallback Mode — curl Reference

Use when MCP tools are unavailable. Credentials are in the subprocess environment as `CLAUDE_PLUGIN_OPTION_*` vars — use these directly in Bash subprocesses.

### Send a notification

```bash
curl -s -X POST "$CLAUDE_PLUGIN_OPTION_GOTIFY_URL/message" \
  -H "X-Gotify-Key: $CLAUDE_PLUGIN_OPTION_GOTIFY_APP_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"title\":\"$TITLE\",\"message\":\"$MESSAGE\",\"priority\":$PRIORITY}"
```

### With markdown

```bash
curl -s -X POST "$CLAUDE_PLUGIN_OPTION_GOTIFY_URL/message" \
  -H "X-Gotify-Key: $CLAUDE_PLUGIN_OPTION_GOTIFY_APP_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"title\":\"$TITLE\",\"message\":\"$MESSAGE\",\"priority\":5,\"extras\":{\"client::display\":{\"contentType\":\"text/markdown\"}}}"
```

### List messages / applications

```bash
# Messages
curl -s "$CLAUDE_PLUGIN_OPTION_GOTIFY_URL/message" \
  -H "X-Gotify-Key: $CLAUDE_PLUGIN_OPTION_GOTIFY_CLIENT_TOKEN"

# Applications
curl -s "$CLAUDE_PLUGIN_OPTION_GOTIFY_URL/application" \
  -H "X-Gotify-Key: $CLAUDE_PLUGIN_OPTION_GOTIFY_CLIENT_TOKEN"
```

### Health check (no auth)

```bash
curl -s "$CLAUDE_PLUGIN_OPTION_GOTIFY_URL/health"
```

### All other management operations (fallback)

For delete, application CRUD, client management — use `GOTIFY_CLIENT_TOKEN` with the appropriate Gotify REST path:

```bash
# Pattern: client token as X-Gotify-Key, method and path per operation
curl -s -X DELETE "$CLAUDE_PLUGIN_OPTION_GOTIFY_URL/message/$MESSAGE_ID" \
  -H "X-Gotify-Key: $CLAUDE_PLUGIN_OPTION_GOTIFY_CLIENT_TOKEN"

curl -s -X POST "$CLAUDE_PLUGIN_OPTION_GOTIFY_URL/application" \
  -H "X-Gotify-Key: $CLAUDE_PLUGIN_OPTION_GOTIFY_CLIENT_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"name\":\"$APP_NAME\"}"
```

---

## Mandatory Automatic Notification Workflows

### 1. Long Running Task Completes (>5 min)

**MCP:**
```
mcp__gotify-mcp__create_message
  app_token: <retrieve via: bash -c 'echo $CLAUDE_PLUGIN_OPTION_GOTIFY_APP_TOKEN'>
  title: "Task Complete"
  message: |
    Project: <basename of cwd>
    Task: <description>
    Session: <session-id if known>
    Status: Completed successfully
  priority: 7
```

**HTTP fallback:**
```bash
curl -s -X POST "$CLAUDE_PLUGIN_OPTION_GOTIFY_URL/message" \
  -H "X-Gotify-Key: $CLAUDE_PLUGIN_OPTION_GOTIFY_APP_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"title\":\"Task Complete\",\"message\":\"Project: $(basename $PWD)\nTask: $TASK_DESC\nStatus: Completed\",\"priority\":7}"
```

### 2. Plan Implementation Finishes

**MCP:**
```
mcp__gotify-mcp__create_message
  app_token: <retrieve via: bash -c 'echo $CLAUDE_PLUGIN_OPTION_GOTIFY_APP_TOKEN'>
  title: "Plan Complete"
  message: |
    Project: <basename of cwd>
    Task: <plan description>
    Status: All steps implemented
    Next: Ready for review
  priority: 7
```

### 3. Blocked — Need User Input

**MCP:**
```
mcp__gotify-mcp__create_message
  app_token: <retrieve via: bash -c 'echo $CLAUDE_PLUGIN_OPTION_GOTIFY_APP_TOKEN'>
  title: "Input Required"
  message: |
    Project: <basename of cwd>
    Task: <current task>
    Blocked: <reason>
    Need: <what you need from user>
  priority: 8
```

### 4. Task Transition — Need Review/Approval

**MCP:**
```
mcp__gotify-mcp__create_message
  app_token: <retrieve via: bash -c 'echo $CLAUDE_PLUGIN_OPTION_GOTIFY_APP_TOKEN'>
  title: "Ready to Proceed"
  message: |
    Project: <basename of cwd>
    Completed: <current phase>
    Next: <next phase>
    Action: Review required before proceeding
  priority: 7
```

---

## Notification Format Requirements

All notifications MUST include:
- **Project/Working Directory**: `basename` of current working directory
- **Task Description**: Specific task completed or blocked on
- **Session ID**: Construct as `session-YYYY-MM-DD-HH-MM` using the current UTC timestamp (e.g. `date -u +session-%Y-%m-%d-%H-%M` in Bash)
- **Status/Next Action**: What's done and what needs user attention

---

## Priority Reference

| Range | Level | Use For |
|-------|-------|---------|
| 0–3   | Low   | Info, FYI |
| 4–7   | Normal | Task updates, completions |
| 8–10  | High  | Blocked, errors, urgent |

---

## Notes

- `create_message` always requires an explicit `app_token` — it is not read from server environment automatically
- Management operations (`get_messages`, `get_applications`, etc.) use `GOTIFY_CLIENT_TOKEN` configured in the server env — no token parameter needed
- `get_health` and `get_version` require no authentication
- Markdown is supported in `message` field for both MCP and HTTP modes
- Confirm notification sent: MCP tools return JSON with message ID on success
