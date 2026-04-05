# Development Workflow

Day-to-day development guide for gotify-mcp.

## Quick start

```bash
git clone https://github.com/jmagar/gotify-mcp.git
cd gotify-mcp
cp .env.example .env
chmod 600 .env
# Edit .env with your Gotify credentials

just dev          # Start dev server
```

## Project structure

```
gotify-mcp/
  gotify_mcp/                # Server source code
    server.py                # FastMCP server, action router, BearerAuth
    services/gotify.py       # Async HTTP client for Gotify REST API
  tests/                     # Unit and integration tests
  scripts/                   # Smoke tests, contract checks, maintenance
  hooks/                     # Claude Code hooks (session start, post-tool)
    scripts/                 # Hook scripts (sync-env, fix-perms, ensure-ignore)
  skills/gotify/             # Skill definition (SKILL.md)
  .claude-plugin/            # Claude Code plugin manifest
  .codex-plugin/             # Codex CLI plugin manifest
  gemini-extension.json      # Gemini CLI manifest
  docker-compose.yml         # Container deployment
  Dockerfile                 # Multi-stage container build
  .env.example               # Environment variable template
  Justfile                   # Task runner recipes
```

## Development cycle

1. Edit source code in `gotify_mcp/`.
2. Run dev server: `just dev`.
3. Test interactively via MCP client or curl:
   ```bash
   curl http://localhost:9158/health
   ```
4. Run checks:
   ```bash
   just lint && just typecheck && just test
   ```
5. Commit with conventional prefix:
   ```bash
   git commit -m "feat(tools): add list_messages filtering"
   ```

## Adding a new tool action

1. Add the action string to the `GOTIFY_ACTIONS` Literal type in `gotify_mcp/server.py`.
2. Add a `case` branch in the `match action:` block in the `gotify` function.
3. Implement the HTTP call in `gotify_mcp/services/gotify.py` as a new method on `GotifyClient`.
4. Add parameters to the `gotify` tool function signature.
5. Update `_HELP_TEXT` in `server.py` with the new action.
6. Update `skills/gotify/SKILL.md` with the new action and examples.
7. Add a test covering success and error cases.

## Debugging

### Log levels

Set `GOTIFY_LOG_LEVEL` in `.env`:

| Level | Use case |
|-------|----------|
| `DEBUG` | Full request/response tracing |
| `INFO` | Startup, tool calls, upstream requests (default) |
| `WARNING` | Missing optional config, degraded conditions |
| `ERROR` | Failures, unhandled exceptions |

### curl testing

```bash
# Health (unauthenticated)
curl http://localhost:9158/health

# MCP Inspector
npx @modelcontextprotocol/inspector
```

Connect to `http://localhost:9158/mcp` with your bearer token.

## Code style

| Tool | Command | Purpose |
|------|---------|---------|
| ruff check | `just lint` | Linting |
| ruff format | `just fmt` | Formatting |
| ty check | `just typecheck` | Type checking |
| pytest | `just test` | Unit tests |

See also: [CONNECT](CONNECT.md) | [PATTERNS](PATTERNS.md) | [TESTS](TESTS.md)
