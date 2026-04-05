# MCP UI Patterns

Protocol-level UI hints for MCP servers to improve client-side rendering.

## Current Status

gotify-mcp does not currently implement `x-ui-*` annotations. The tool schema uses standard JSON Schema with `Literal` enum types for action selection. All responses are JSON strings consumed by LLM clients.

## Potential UI Enhancements

If MCP UI annotations are adopted, gotify-mcp could benefit from:

### Action selector

```json
{
  "action": {
    "type": "string",
    "enum": ["send_message", "list_messages", "health", ...],
    "x-ui-widget": "select"
  }
}
```

### Conditional fields

Show `app_token` and `message` only when `action` is `send_message`:

```json
{
  "app_token": {
    "type": "string",
    "x-ui-condition": {"action": ["send_message"]}
  },
  "message": {
    "type": "string",
    "x-ui-widget": "textarea",
    "x-ui-condition": {"action": ["send_message"]}
  }
}
```

### Priority selector

```json
{
  "priority": {
    "type": "integer",
    "x-ui-widget": "slider",
    "minimum": 0,
    "maximum": 10,
    "x-ui-condition": {"action": ["send_message"]}
  }
}
```

## Response Formatting

Current responses are JSON strings. Future versions could include rendering hints:

| Hint | Use case |
|------|----------|
| `table` | `list_messages`, `list_applications`, `list_clients` results |
| `json` | `health`, `version`, `current_user` results |

## Future Direction

MCP UI is an emerging specification. gotify-mcp will adopt annotations when the spec stabilizes and client support is widespread.

See also: [WEBMCP](WEBMCP.md) | [TOOLS](TOOLS.md) | [SCHEMA](SCHEMA.md)
