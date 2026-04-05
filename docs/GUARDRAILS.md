# Security Guardrails — gotify-mcp

Safety and security patterns enforced across the plugin.

## Credential management

### Storage

- All credentials in `.env` with `chmod 600` permissions
- Never commit `.env` or any file containing secrets
- Use `.env.example` as a tracked template with placeholder values only
- Generate tokens with `openssl rand -hex 32`

### Gotify dual-token security

Gotify uses separate tokens for separate concerns:

| Token | Scope | Risk if leaked |
| --- | --- | --- |
| App token | Can only send messages to one application | Low — messages only |
| Client token | Can read all messages, manage all apps and clients | High — full management access |

Keep the client token restricted. Prefer app tokens when only sending notifications.

### Ignore files

`.gitignore` and `.dockerignore` must include:

```
.env
*.secret
credentials.*
*.pem
*.key
```

### Hook enforcement

Hooks verify security invariants at session start and after file operations:

| Hook | Trigger | Purpose |
| --- | --- | --- |
| `sync-env.sh` | SessionStart | Syncs `userConfig` credentials to `.env` with file locking |
| `fix-env-perms.sh` | PostToolUse (Write/Edit/Bash) | Sets `.env` to `chmod 600` if present |
| `ensure-ignore-files.sh` | SessionStart | Verifies `.gitignore` and `.dockerignore` contain required patterns |

### Credential rotation

1. Generate new token: `openssl rand -hex 32`
2. Update `.env` with new value
3. Restart the server: `just restart`
4. Update MCP client configuration with new token
5. Verify: `just health`

## Destructive operations

Four actions are gated behind a confirmation check:

- `delete_message`
- `delete_all_messages`
- `delete_application`
- `delete_client`

Without `confirm=True`, the server returns:

```json
"Destructive operation. Pass confirm=True to proceed."
```

Server-wide bypass via `ALLOW_DESTRUCTIVE=true` or `ALLOW_YOLO=true` (automated environments only).

## Docker security

### Non-root execution

The container runs as non-root (UID/GID 1000 by default):

```dockerfile
RUN groupadd --gid 1000 mcpuser && \
    useradd --uid 1000 --gid mcpuser --shell /bin/bash --create-home mcpuser
USER 1000:1000
```

Override with `PUID` and `PGID` environment variables.

### No baked environment

The Docker image contains no credentials at build time:

- No `ENV GOTIFY_CLIENT_TOKEN=...` in Dockerfile
- No `COPY .env` in Dockerfile
- Credentials injected at runtime via `env_file` in docker-compose.yml

Verify with:

```bash
docker inspect gotify-mcp:latest | jq '.[0].Config.Env'
```

### Image scanning

CI runs Trivy scans on every image push:

```bash
docker scout cves gotify-mcp:latest
```

## Network security

### HTTPS in production

- `GOTIFY_URL` should use `https://` in production
- Use valid TLS certificates (Let's Encrypt via SWAG or similar)
- HTTP is acceptable only for local development

### Bearer token authentication

- HTTP transport requires `GOTIFY_MCP_TOKEN` by default
- Token sent as `Authorization: Bearer <token>` header
- Timing-safe comparison via `hmac.compare_digest`
- Disable only behind a trusted reverse proxy (`GOTIFY_MCP_NO_AUTH=true`)

### Health endpoint

- `/health` is unauthenticated — required for container liveness probes
- Returns only status information, never credentials or internal state
- All other endpoints require bearer authentication

## Input handling

### Response truncation

- Responses truncated at 512 KB
- Append `... [truncated]` marker to indicate truncation
- Prevents unbounded upstream responses from consuming MCP context

### Docker URL rewriting

When running inside Docker, `localhost` and `127.0.0.1` in `GOTIFY_URL` are automatically rewritten to `host.docker.internal` so the container can reach a host-side Gotify server.

## Logging

- Never log credentials, tokens, or API keys — not even at DEBUG level
- Startup banner masks token presence: `GOTIFY_MCP_TOKEN: SET` / `NOT SET`
- Log file permissions are restrictive
- Rotate logs to prevent disk exhaustion (5 MB max, 3 backups)
