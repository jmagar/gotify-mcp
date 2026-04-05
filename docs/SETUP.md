# Setup Guide — gotify-mcp

Step-by-step instructions to get gotify-mcp running locally, in Docker, or as a Claude Code plugin.

## Prerequisites

| Dependency | Version | Purpose |
| --- | --- | --- |
| Python | 3.12+ | Runtime |
| uv | latest | Package manager |
| Docker | 24+ | Container deployment |
| Docker Compose | v2+ | Orchestration |
| just | latest | Task runner |
| openssl | any | Token generation |

You also need a running Gotify server with at least one application token and one client token.

## 1. Clone the repository

```bash
git clone https://github.com/jmagar/gotify-mcp.git
cd gotify-mcp
```

## 2. Install dependencies

```bash
uv sync --dev
```

Or use the setup recipe:

```bash
just setup
```

## 3. Configure environment

```bash
cp .env.example .env
chmod 600 .env
```

Edit `.env` and set required values:

```bash
# Gotify server
GOTIFY_URL=https://gotify.example.com
GOTIFY_CLIENT_TOKEN=your_client_token_here
GOTIFY_APP_TOKEN=your_app_token_here

# MCP server auth token — generate one:
#   openssl rand -hex 32
GOTIFY_MCP_TOKEN=<paste-generated-token>
```

See [CONFIG](CONFIG.md) for all environment variables.

### Where to find Gotify tokens

| Token | Location in Gotify UI |
| --- | --- |
| App token | Settings > Apps > Create Application > copy the token |
| Client token | Settings > Clients > Create Client > copy the token |

App tokens can only send messages. Client tokens can read messages and manage resources.

## 4. Start locally

```bash
just dev
```

Or directly:

```bash
uv run python -m gotify_mcp.server
```

The server starts on `http://localhost:9158` by default.

## 5. Start via Docker

```bash
just up
```

Or manually:

```bash
docker compose up -d
```

## 6. Verify

```bash
just health
```

Or:

```bash
curl http://localhost:9158/health
```

Expected response:

```json
{"status": "ok", "gotify": {"health": "green", "database": "ok"}}
```

## 7. Install as Claude Code plugin

```bash
/plugin marketplace add jmagar/claude-homelab
/plugin install gotify-mcp @jmagar-claude-homelab
```

Configure the plugin with your MCP token and Gotify credentials when prompted.

## Troubleshooting

### "Connection refused" on health check

- Confirm the server is running: `docker compose ps` or check process list
- Verify `GOTIFY_MCP_PORT` matches the port you are curling (default: 9158)
- If running in Docker, ensure the port is published in `docker-compose.yml`

### "401 Unauthorized" on tool calls

- Verify `GOTIFY_MCP_TOKEN` in `.env` matches the token configured in your MCP client
- If behind a reverse proxy, set `GOTIFY_MCP_NO_AUTH=true` and handle auth at the proxy
- Confirm you are using the right Gotify token type: app token for sending, client token for management

### "GOTIFY_URL must be set" at startup

- Confirm `.env` exists and is readable: `ls -la .env`
- Confirm `GOTIFY_URL` is set: `grep GOTIFY_URL .env`
- Check file permissions: `chmod 600 .env`

### Docker cannot reach Gotify server

- `localhost` in `GOTIFY_URL` does not resolve inside the container
- The server automatically rewrites `localhost`/`127.0.0.1` to `host.docker.internal`
- If that does not work, use the Gotify server's LAN IP directly

### Plugin not discovered by Claude Code

- Run `/plugin list` and confirm the plugin appears
- Check `~/.claude/plugins/cache/` for the plugin directory
- Re-run `/plugin marketplace add jmagar/claude-homelab` to refresh
