# MCP Tools Reference

## Design Philosophy

gotify-mcp exposes exactly two MCP tools:

| Tool | Purpose | Parameters |
|------|---------|------------|
| `gotify` | Primary tool — flat action dispatch | `action`, plus action-specific params |
| `gotify_help` | Returns markdown reference for all actions | _(none)_ |

This 2-tool pattern keeps the MCP surface small while supporting 14 distinct operations. Clients call `gotify_help` first to discover available actions, then call `gotify` with the appropriate action.

## Primary Tool: `gotify`

### Input Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `action` | enum | yes | Operation to perform (see Actions below) |
| `app_token` | string | no | App token for `send_message` |
| `message` | string | no | Message body for `send_message` |
| `title` | string | no | Message title |
| `priority` | integer | no | Priority 0-10 |
| `extras` | dict | no | Extended metadata (e.g., Markdown content type) |
| `message_id` | integer | no | Target message ID for `delete_message` |
| `app_id` | integer | no | Application ID for filtering or targeting |
| `client_id` | integer | no | Client ID for `delete_client` |
| `name` | string | no | Name for creating apps/clients |
| `description` | string | no | Description for apps |
| `default_priority` | integer | no | Default priority for apps |
| `offset` | integer | no | Pagination offset (default: 0) |
| `limit` | integer | no | Max items to return (default: 50) |
| `sort_by` | string | no | Sort field (default: "id") |
| `sort_order` | string | no | "asc" or "desc" (default: "desc") |
| `query` | string | no | Substring filter |
| `confirm` | boolean | no | Required `True` for destructive actions |

### Actions

| Action | Description | Required Params | Destructive |
|--------|-------------|-----------------|-------------|
| `send_message` | Send a push notification | `app_token`, `message` | no |
| `list_messages` | List messages with pagination | — | no |
| `delete_message` | Delete one message | `message_id`, `confirm` | yes |
| `delete_all_messages` | Delete all messages | `confirm` | yes |
| `list_applications` | List all applications | — | no |
| `create_application` | Create a new application | `name` | no |
| `update_application` | Update an application | `app_id` | no |
| `delete_application` | Delete an application | `app_id`, `confirm` | yes |
| `list_clients` | List all clients | — | no |
| `create_client` | Create a new client | `name` | no |
| `delete_client` | Delete a client | `client_id`, `confirm` | yes |
| `health` | Gotify server health | — | no |
| `version` | Gotify server version | — | no |
| `current_user` | Current user info | — | no |

### Response Format

All responses are JSON strings. Successful responses contain the upstream Gotify API response. Error responses follow this structure:

```json
{
  "error": "Short error identifier",
  "errorCode": 401,
  "errorDescription": "Human-readable explanation"
}
```

Responses are truncated at 512 KB with a `... [truncated]` marker.

## Help Tool: `gotify_help`

Takes no parameters. Returns a markdown document listing all actions, parameters, and usage examples.

## Destructive Operations

Operations that delete data require `confirm=True`:

1. Client calls with destructive action without confirmation
2. Server returns: `"Destructive operation. Pass confirm=True to proceed."`
3. Client re-calls with `confirm=True`
4. Server executes the operation

Set `ALLOW_DESTRUCTIVE=true` or `ALLOW_YOLO=true` to skip confirmation globally.

## Example Tool Calls

```python
# Send a notification
gotify(action="send_message", app_token="AbCdEf", message="Build finished", priority=5)

# Send with Markdown
gotify(action="send_message", app_token="AbCdEf", title="Deploy complete",
       message="## Status\n- All steps done",
       extras={"client::display": {"contentType": "text/markdown"}})

# List messages with filtering
gotify(action="list_messages", app_id=3, query="error", limit=10)

# Delete with confirmation
gotify(action="delete_message", message_id=42, confirm=True)

# Health check
gotify(action="health")
```

## See Also

- [SCHEMA.md](SCHEMA.md) — Schema definitions behind these tools
- [AUTH.md](AUTH.md) — Authentication required before tool calls
- [ENV.md](ENV.md) — Safety gate environment variables
