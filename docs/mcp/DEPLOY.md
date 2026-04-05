# Deployment Guide

Deployment patterns for `gotify-mcp`. Choose the method that fits your environment.

## Local Development

```bash
uv sync && uv run python -m gotify_mcp.server
```

Shortcut:

```bash
just dev
```

The server starts on `http://localhost:9158` by default.

## Package Manager

```bash
pip install gotify-mcp
gotify-mcp-server
```

Or via `uvx`:

```bash
uvx gotify-mcp
```

## Docker

### Build

Multi-stage Dockerfile: builder installs dependencies with uv, runtime copies only the venv.

```bash
docker build -t gotify-mcp .
```

### Compose

```yaml
services:
  gotify-mcp:
    build: .
    container_name: gotify-mcp
    user: "${PUID:-1000}:${PGID:-1000}"
    ports:
      - "${GOTIFY_MCP_PORT:-9158}:${GOTIFY_MCP_PORT:-9158}"
    env_file:
      - ~/.claude-homelab/.env
    volumes:
      - gotify-mcp-logs:/app/logs
    restart: unless-stopped
    deploy:
      resources:
        limits:
          cpus: "0.5"
          memory: 256M
    healthcheck:
      test: ["CMD", "python", "-c", "import os,sys,urllib.request; port=os.environ.get('GOTIFY_MCP_PORT','9158'); urllib.request.urlopen(f'http://localhost:{port}/health',timeout=5); sys.exit(0)"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 30s
    networks:
      - jakenet
```

```bash
docker compose up -d
```

### Container Conventions

| Concern | Pattern |
|---------|---------|
| Base image | `python:3.12-slim` (builder and runtime) |
| User | Non-root, UID 1000 (`mcpuser`) |
| Health check | Python urllib to `http://localhost:9158/health` every 30s |
| Logs | Named volume `gotify-mcp-logs` at `/app/logs` |
| Network | External `jakenet` |
| Resources | 0.5 CPU, 256 MB RAM limits |

### Entrypoint

`entrypoint.sh` validates required environment variables before starting:

1. Checks `GOTIFY_URL` is set (exits if not)
2. Checks `GOTIFY_MCP_TOKEN` is set when HTTP transport without no-auth (exits if not)
3. Warns if `GOTIFY_CLIENT_TOKEN` is missing
4. Exports defaults for optional variables
5. Starts the server with `exec python -m gotify_mcp.server`

### Docker URL Rewriting

When running inside Docker, `localhost` and `127.0.0.1` in `GOTIFY_URL` are automatically rewritten to `host.docker.internal`. This allows the container to reach a Gotify server running on the host.

## Port Assignment

| Service | Default Port | Env Var |
|---------|-------------|---------|
| gotify-mcp | 9158 | `GOTIFY_MCP_PORT` |

## Related Docs

- [ENV.md](ENV.md) — environment variables
- [LOGS.md](LOGS.md) — logging configuration
- [CONNECT.md](CONNECT.md) — client connection methods
