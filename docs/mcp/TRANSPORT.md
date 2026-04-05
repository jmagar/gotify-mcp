# Transport Methods Reference

## Overview

gotify-mcp supports two transport methods for MCP communication:

| Transport | Auth | Use Case | Config Value |
|-----------|------|----------|--------------|
| stdio | None (process isolation) | Claude Desktop, Codex CLI | `stdio` |
| Streamable-HTTP | Bearer token | Docker, remote servers | `http` |

Set the transport via:

```env
GOTIFY_MCP_TRANSPORT=http  # default
```

## stdio

JSON-RPC messages over stdin/stdout. No network listener, no auth required — the parent process owns the communication channel.

```env
GOTIFY_MCP_TRANSPORT=stdio
```

### Claude Desktop Configuration

`~/.claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "gotify-mcp": {
      "command": "uvx",
      "args": ["gotify-mcp"],
      "env": {
        "GOTIFY_URL": "https://gotify.example.com",
        "GOTIFY_CLIENT_TOKEN": "your-client-token",
        "GOTIFY_MCP_TRANSPORT": "stdio"
      }
    }
  }
}
```

### When to Use

- Local development with Claude Desktop or Codex CLI
- Single-user setups where the MCP server runs as a child process
- No network exposure needed

## Streamable-HTTP

HTTP server with streaming support. Requires bearer token authentication. This is the default transport.

```env
GOTIFY_MCP_TRANSPORT=http
GOTIFY_MCP_HOST=0.0.0.0
GOTIFY_MCP_PORT=9158
GOTIFY_MCP_TOKEN=your-token-here
```

### Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/mcp` | POST | MCP JSON-RPC with streaming responses |
| `/health` | GET | Health check (unauthenticated) |

### Claude Code Configuration

`.claude/mcp.json`:

```json
{
  "mcpServers": {
    "gotify-mcp": {
      "type": "http",
      "url": "http://localhost:9158/mcp",
      "headers": {
        "Authorization": "Bearer your-token-here"
      }
    }
  }
}
```

### When to Use

- Docker deployments
- Remote/shared MCP server
- Multiple clients connecting to one server
- Behind a reverse proxy (SWAG, nginx, Caddy)

## Transport Selection Guide

```
Local dev with Claude Desktop?
  -> stdio (no setup needed)

Running in Docker or on a remote host?
  -> http (streamable-http, default)

Behind a reverse proxy with its own auth?
  -> http + GOTIFY_MCP_NO_AUTH=true
```

## Port Assignment

| Service | Default Port |
|---------|-------------|
| gotify-mcp | 9158 |

## See Also

- [AUTH.md](AUTH.md) — Bearer token setup for HTTP transport
- [ENV.md](ENV.md) — Transport-related environment variables
