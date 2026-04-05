# Connect to MCP

How to connect to the gotify-mcp server from every supported client and transport.

## Automatically via plugin

The simplest path. The plugin manifest handles transport, auth, and tool registration.

```bash
# Claude Code
/plugin marketplace add jmagar/gotify-mcp
```

No further configuration needed — the manifest wires HTTP transport and tool permissions.

## Claude Code CLI

### stdio

```bash
claude mcp add gotify-mcp -- uvx gotify-mcp
```

### HTTP

```bash
claude mcp add --transport http gotify-mcp http://localhost:9158/mcp
```

With bearer auth:

```bash
claude mcp add --transport http \
  --header "Authorization: Bearer $GOTIFY_MCP_TOKEN" \
  gotify-mcp http://localhost:9158/mcp
```

### Scopes

| Flag | Scope | Config file |
|------|-------|-------------|
| `--scope project` | Current project only | `.claude/settings.local.json` |
| `--scope user` | All projects (local) | `~/.claude/settings.json` |
| _(none)_ | Defaults to project | `.claude/settings.local.json` |

## Codex CLI

### stdio

`.codex/mcp.json`:

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

### HTTP

```json
{
  "mcpServers": {
    "gotify-mcp": {
      "type": "http",
      "url": "http://localhost:9158/mcp",
      "headers": {
        "Authorization": "Bearer ${GOTIFY_MCP_TOKEN}"
      }
    }
  }
}
```

## Gemini CLI

### stdio

In `gemini-extension.json` (project root or `~/.gemini/`):

```json
{
  "mcpServers": {
    "gotify-mcp": {
      "command": "uv",
      "args": ["run", "gotify-mcp-server"],
      "cwd": "${extensionPath}"
    }
  }
}
```

## Config file locations

| Client | Scope | File |
|--------|-------|------|
| Claude Code | Project | `.claude/settings.local.json` |
| Claude Code | User | `~/.claude/settings.json` |
| Codex CLI | Project | `.codex/mcp.json` |
| Codex CLI | User | `~/.codex/mcp.json` |
| Gemini CLI | Project | `gemini-extension.json` |
| Gemini CLI | Global | `~/.gemini/gemini-extension.json` |

## Verifying connection

After configuring, verify the server is reachable:

```bash
# HTTP health check (unauthenticated)
curl -s http://localhost:9158/health
# Expected: {"status":"ok","gotify":{...}}

# Test a tool call via Claude Code
claude "call gotify_help()"
```

If connection fails, check:

1. Server is running (`just up` or `just dev`)
2. Port `9158` is not blocked by firewall
3. Bearer token matches between client config and server `.env`
4. For stdio: `uvx` is on PATH and `GOTIFY_MCP_TRANSPORT=stdio` is set

See also: [AUTH](AUTH.md) | [ENV](ENV.md) | [TRANSPORT](TRANSPORT.md)
