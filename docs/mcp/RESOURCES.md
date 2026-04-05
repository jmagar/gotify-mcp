# MCP Resources Reference

## Overview

gotify-mcp does not currently expose MCP resources. All operations are performed through the `gotify` tool via action dispatch.

## Planned Resources

Future versions may expose read-only resources for common queries:

| URI | Description | Status |
|-----|-------------|--------|
| `gotify://application/{app_id}/messages` | Messages for a specific app | Planned |
| `gotify://currentuser` | Current authenticated user info | Planned |

These URIs are referenced in the skill definition but are not yet implemented as MCP resource handlers.

## When to Use Resources vs Tools

Use **resources** when:
- Reading current state without side effects
- Providing context to the LLM without tool invocation overhead

Use **tools** when:
- Creating, updating, or deleting data
- Performing parameterized queries (filtering, pagination, sorting)

Currently, all Gotify operations go through the `gotify` tool, which handles both reads and writes.

## See Also

- [TOOLS.md](TOOLS.md) — All operations via the `gotify` tool
- [SCHEMA.md](SCHEMA.md) — Tool schema definitions
