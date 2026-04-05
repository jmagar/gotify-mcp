# Tool Schema Documentation

## Overview

Tool schemas define the input validation contract for MCP tools. In gotify-mcp, schemas are defined using Python type annotations and FastMCP's automatic schema generation.

## Schema Definition

The `gotify` tool uses Python type annotations directly on the function signature:

```python
GOTIFY_ACTIONS = Literal[
    "send_message", "list_messages", "delete_message", "delete_all_messages",
    "list_applications", "create_application", "update_application", "delete_application",
    "list_clients", "create_client", "delete_client",
    "health", "version", "current_user",
]

@mcp.tool()
async def gotify(
    action: GOTIFY_ACTIONS,
    subaction: str = "",
    app_token: str = "",
    message: str = "",
    title: str = "",
    priority: int | None = None,
    message_id: int | None = None,
    extras: dict[str, Any] | None = None,
    app_id: int | None = None,
    name: str = "",
    description: str = "",
    default_priority: int | None = None,
    client_id: int | None = None,
    offset: int = 0,
    limit: int = 50,
    sort_by: str = "id",
    sort_order: str = "desc",
    query: str = "",
    confirm: bool = False,
) -> str:
```

FastMCP automatically generates a JSON Schema from this signature and exposes it via the `tools/list` MCP method.

## JSON Schema Output

The generated schema for the `gotify` tool:

```json
{
  "type": "object",
  "properties": {
    "action": {
      "type": "string",
      "enum": [
        "send_message", "list_messages", "delete_message", "delete_all_messages",
        "list_applications", "create_application", "update_application", "delete_application",
        "list_clients", "create_client", "delete_client",
        "health", "version", "current_user"
      ]
    },
    "app_token": { "type": "string", "default": "" },
    "message": { "type": "string", "default": "" },
    "title": { "type": "string", "default": "" },
    "priority": { "type": "integer", "nullable": true },
    "message_id": { "type": "integer", "nullable": true },
    "extras": { "type": "object", "nullable": true },
    "app_id": { "type": "integer", "nullable": true },
    "name": { "type": "string", "default": "" },
    "description": { "type": "string", "default": "" },
    "default_priority": { "type": "integer", "nullable": true },
    "client_id": { "type": "integer", "nullable": true },
    "offset": { "type": "integer", "default": 0 },
    "limit": { "type": "integer", "default": 50 },
    "sort_by": { "type": "string", "default": "id" },
    "sort_order": { "type": "string", "default": "desc" },
    "query": { "type": "string", "default": "" },
    "confirm": { "type": "boolean", "default": false }
  },
  "required": ["action"]
}
```

The `gotify_help` tool takes no parameters — its schema is an empty object.

## Input Validation

FastMCP validates inputs before dispatch:
- Missing `action` returns a validation error
- Invalid `action` enum values are caught by the `match` statement and return a helpful error
- Type mismatches (e.g., string where integer expected) are rejected

## See Also

- [TOOLS.md](TOOLS.md) — Tool behavior documentation
- [RESOURCES.md](RESOURCES.md) — Resource data shapes
