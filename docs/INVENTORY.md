# Component Inventory — gotify-mcp

Complete listing of all plugin components.

## MCP tools

| Tool | Action | Description | Destructive |
| --- | --- | --- | --- |
| `gotify` | `send_message` | Send a push notification | no |
| `gotify` | `list_messages` | List messages with pagination and filtering | no |
| `gotify` | `delete_message` | Delete one message | yes |
| `gotify` | `delete_all_messages` | Delete all messages | yes |
| `gotify` | `list_applications` | List registered applications | no |
| `gotify` | `create_application` | Create a new application | no |
| `gotify` | `update_application` | Update an existing application | no |
| `gotify` | `delete_application` | Delete an application and its messages | yes |
| `gotify` | `list_clients` | List registered clients | no |
| `gotify` | `create_client` | Create a new client | no |
| `gotify` | `delete_client` | Delete a client | yes |
| `gotify` | `health` | Check Gotify server health | no |
| `gotify` | `version` | Get Gotify server version | no |
| `gotify` | `current_user` | Get current authenticated user info | no |
| `gotify_help` | — | Return action reference as Markdown | no |

## Environment variables

| Variable | Required | Default | Sensitive |
| --- | --- | --- | --- |
| `GOTIFY_URL` | yes | — | no |
| `GOTIFY_CLIENT_TOKEN` | yes* | — | yes |
| `GOTIFY_APP_TOKEN` | no | — | yes |
| `GOTIFY_MCP_HOST` | no | `0.0.0.0` | no |
| `GOTIFY_MCP_PORT` | no | `9158` | no |
| `GOTIFY_MCP_TOKEN` | yes** | — | yes |
| `GOTIFY_MCP_TRANSPORT` | no | `http` | no |
| `GOTIFY_MCP_NO_AUTH` | no | `false` | no |
| `GOTIFY_LOG_LEVEL` | no | `INFO` | no |
| `ALLOW_DESTRUCTIVE` | no | `false` | no |
| `ALLOW_YOLO` | no | `false` | no |
| `PUID` | no | `1000` | no |
| `PGID` | no | `1000` | no |
| `DOCKER_NETWORK` | no | — | no |

## Plugin surfaces

| Surface | Present | Path |
| --- | --- | --- |
| Skills | yes | `skills/gotify/SKILL.md` |
| Agents | no | — |
| Commands | no | — |
| Hooks | yes | `hooks/hooks.json` |
| Channels | no | — |
| Output styles | no | — |
| Schedules | no | — |

## Docker

| Component | Value |
| --- | --- |
| Image | `ghcr.io/jmagar/gotify-mcp:latest` |
| Port | `9158` |
| Health endpoint | `GET /health` (unauthenticated) |
| Compose file | `docker-compose.yml` |
| Entrypoint | `entrypoint.sh` |
| User | `1000:1000` |
| Resource limits | 0.5 CPU, 256 MB RAM |

## CI/CD workflows

| Workflow | Trigger | Purpose |
| --- | --- | --- |
| `ci.yml` | push, PR | Lint, typecheck, test, audit, contract drift, Docker security, MCP integration |
| `docker-publish.yml` | push to main, tags | Build and publish multi-arch Docker image to GHCR |
| `publish-pypi.yml` | tag push (`v*.*.*`) | Build, publish to PyPI, create GitHub Release, publish to MCP Registry |

## Scripts

| Script | Location | Purpose |
| --- | --- | --- |
| `lint-plugin.sh` | `scripts/` | Validate plugin manifests and version sync |
| `check-docker-security.sh` | `scripts/` | Lint Dockerfile for security issues |
| `check-no-baked-env.sh` | `scripts/` | Verify no baked env vars in Docker image |
| `ensure-ignore-files.sh` | `scripts/` | Confirm ignore files include required patterns |
| `check-outdated-deps.sh` | `scripts/` | Report outdated dependencies |
| `smoke-test.sh` | `scripts/` | Smoke test against running server |
| `test_live.sh` | `tests/` | Live integration test suite |
| `sync-env.sh` | `hooks/scripts/` | Sync userConfig to .env |
| `fix-env-perms.sh` | `hooks/scripts/` | Enforce chmod 600 on .env |
| `ensure-ignore-files.sh` | `hooks/scripts/` | Keep ignore files aligned |

## Dependencies

### Runtime

| Package | Version | Purpose |
| --- | --- | --- |
| `fastmcp` | >=3.2.0 | MCP server framework |
| `httpx` | >=0.28.1 | Async HTTP client for Gotify API |
| `python-dotenv` | >=1.1.0 | Environment variable loading |

### Development

| Package | Version | Purpose |
| --- | --- | --- |
| `ruff` | >=0.9.0 | Linter and formatter |
| `ty` | >=0.0.1a6 | Type checker |
| `pytest` | >=8.0.0 | Test framework |
| `pytest-asyncio` | >=0.25.0 | Async test support |
