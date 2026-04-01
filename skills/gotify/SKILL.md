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

## Tools

This skill exposes two MCP tools: `gotify` (action router) and `gotify_help`.

### `gotify` — Action Router

Manages Gotify push notifications, messages, applications, clients, and server info through a unified action+subaction interface.

```
gotify(action, subaction, **params)
```

**Always prefer MCP mode** (`gotify(...)` tool calls). Fall back to HTTP only when MCP tools are unavailable.

**MCP URL**: `${user_config.gotify_mcp_url}`

---

### `gotify_help` — Help and Discovery

Returns documentation, available actions, parameter reference, and examples.

```
gotify_help()
gotify_help(action="message")   # help for a specific action
```

---

## Action Reference

### action="message"

Manages push notification messages.

| subaction | description | key params |
|-----------|-------------|------------|
| `send`    | Send a push notification | `app_token` (required), `message` (required), `title`, `priority` (0–10), `extras` |
| `list`    | List recent messages | `limit` (1–200, default 100), `since` (pagination cursor) |
| `delete`  | Delete a single message | `message_id` (required) |
| `delete_all` | Delete all messages | — |

**Examples:**

```python
# Send a notification
gotify(action="message", subaction="send",
       app_token="<token>",
       title="Task Complete",
       message="Project: gotify-mcp\nStatus: done",
       priority=7)

# Send with markdown
gotify(action="message", subaction="send",
       app_token="<token>",
       title="Plan Complete",
       message="## Summary\n- All steps implemented\n- Ready for review",
       priority=7,
       extras={"client::display": {"contentType": "text/markdown"}})

# List messages
gotify(action="message", subaction="list", limit=20)

# Delete a message
gotify(action="message", subaction="delete", message_id=42)

# Delete all messages
gotify(action="message", subaction="delete_all")
```

The `app_token` for `send` is passed **per call** — it is NOT read from the server env. Retrieve it first via a Bash subprocess:

```bash
echo "$CLAUDE_PLUGIN_OPTION_GOTIFY_APP_TOKEN"
```

If the variable is empty, report a configuration error — the `gotify_app_token` userConfig field has not been set.

---

### action="application"

Manages Gotify applications (sources for push notifications).

| subaction | description | key params |
|-----------|-------------|------------|
| `list`    | List all applications | — |
| `create`  | Create a new application | `name` (required), `description`, `default_priority` |
| `update`  | Update an existing application | `app_id` (required), `name`, `description`, `default_priority` |
| `delete`  | Delete an application | `app_id` (required) |

**Examples:**

```python
# List applications
gotify(action="application", subaction="list")

# Create an application
gotify(action="application", subaction="create",
       name="homelab-alerts",
       description="Claude Code homelab notifications",
       default_priority=5)

# Update an application
gotify(action="application", subaction="update",
       app_id=3, name="homelab-alerts-v2", default_priority=7)

# Delete an application
gotify(action="application", subaction="delete", app_id=3)
```

---

### action="client"

Manages Gotify clients (subscribers that receive notifications).

| subaction | description | key params |
|-----------|-------------|------------|
| `list`    | List all clients | — |
| `create`  | Create a new client | `name` (required) |

**Examples:**

```python
# List clients
gotify(action="client", subaction="list")

# Create a client
gotify(action="client", subaction="create", name="my-phone")
```

---

### action="server"

Retrieves server health and version information. Note: MCP tool calls still require bearer authentication. Only the raw `/health` HTTP endpoint is unauthenticated.

| subaction | description | key params |
|-----------|-------------|------------|
| `health`  | Check server health | — |
| `version` | Get server version | — |

**Examples:**

```python
# Health check
gotify(action="server", subaction="health")

# Version info
gotify(action="server", subaction="version")
```

---

## Resources

```
gotify://application/{app_id}/messages   — messages for a specific app
gotify://currentuser                     — current authenticated user info
```

---

## HTTP Fallback Mode

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

### Management operations (fallback)

```bash
# Delete a message
curl -s -X DELETE "$CLAUDE_PLUGIN_OPTION_GOTIFY_URL/message/$MESSAGE_ID" \
  -H "X-Gotify-Key: $CLAUDE_PLUGIN_OPTION_GOTIFY_CLIENT_TOKEN"

# Create application
curl -s -X POST "$CLAUDE_PLUGIN_OPTION_GOTIFY_URL/application" \
  -H "X-Gotify-Key: $CLAUDE_PLUGIN_OPTION_GOTIFY_CLIENT_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"name\":\"$APP_NAME\"}"
```

---

## Mandatory Automatic Notification Workflows

### 1. Long Running Task Completes (>5 min)

```python
gotify(action="message", subaction="send",
       app_token="<retrieve via: bash -c 'echo $CLAUDE_PLUGIN_OPTION_GOTIFY_APP_TOKEN'>",
       title="Task Complete",
       message="Project: <basename of cwd>\nTask: <description>\nSession: <session-YYYY-MM-DD-HH-MM>\nStatus: Completed successfully",
       priority=7)
```

### 2. Plan Implementation Finishes

```python
gotify(action="message", subaction="send",
       app_token="<retrieve via: bash -c 'echo $CLAUDE_PLUGIN_OPTION_GOTIFY_APP_TOKEN'>",
       title="Plan Complete",
       message="Project: <basename of cwd>\nTask: <plan description>\nStatus: All steps implemented\nNext: Ready for review",
       priority=7)
```

### 3. Blocked — Need User Input

```python
gotify(action="message", subaction="send",
       app_token="<retrieve via: bash -c 'echo $CLAUDE_PLUGIN_OPTION_GOTIFY_APP_TOKEN'>",
       title="Input Required",
       message="Project: <basename of cwd>\nTask: <current task>\nBlocked: <reason>\nNeed: <what you need from user>",
       priority=8)
```

### 4. Task Transition — Need Review/Approval

```python
gotify(action="message", subaction="send",
       app_token="<retrieve via: bash -c 'echo $CLAUDE_PLUGIN_OPTION_GOTIFY_APP_TOKEN'>",
       title="Ready to Proceed",
       message="Project: <basename of cwd>\nCompleted: <current phase>\nNext: <next phase>\nAction: Review required before proceeding",
       priority=7)
```

---

## Notification Format Requirements

All notifications MUST include:
- **Project/Working Directory**: `basename` of current working directory
- **Task Description**: Specific task completed or blocked on
- **Session ID**: Construct as `session-YYYY-MM-DD-HH-MM` using current UTC timestamp (`date -u +session-%Y-%m-%d-%H-%M`)
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

- `gotify(action="message", subaction="send")` always requires an explicit `app_token` — it is not read from server environment automatically
- Management operations (`list`, `delete`, application/client CRUD) use `GOTIFY_CLIENT_TOKEN` configured in the server env — no token parameter needed
- `gotify(action="server", subaction="health")` and `gotify(action="server", subaction="version")` require no authentication
- Markdown is supported in the `message` field for both MCP and HTTP modes
- Confirm notification sent: `gotify(...)` returns JSON with message ID on success
