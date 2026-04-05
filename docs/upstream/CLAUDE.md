# Upstream Service Integration — gotify-mcp

How gotify-mcp integrates with the Gotify push notification API.

## Purpose

gotify-mcp is an MCP server that wraps the Gotify REST API, exposing push notification and management functionality as MCP tools consumable by Claude Code, Codex, and Gemini.

## API access pattern

```
GET/POST/PUT/DELETE https://gotify.example.com/<endpoint>
X-Gotify-Key: <token>
```

Gotify uses the `X-Gotify-Key` header for authentication, not `Authorization: Bearer`.

## Dual-token authentication

Gotify distinguishes between two token types:

| Token | Header | Endpoints | Scope |
| --- | --- | --- | --- |
| App token | `X-Gotify-Key: <app_token>` | `POST /message` | Send messages to one application |
| Client token | `X-Gotify-Key: <client_token>` | All management endpoints | Read messages, manage apps/clients, user info |

Using the wrong token type returns 401 from the upstream server. The `GotifyClient` selects the token per request:
- `send_message()` accepts an explicit `app_token` parameter
- All other methods use `self.client_token` (from `GOTIFY_CLIENT_TOKEN`)

## Endpoints used

| Method | Endpoint | Token | MCP Action |
| --- | --- | --- | --- |
| POST | `/message` | app | `send_message` |
| GET | `/message` | client | `list_messages` |
| GET | `/application/{id}/message` | client | `list_messages` (filtered) |
| DELETE | `/message/{id}` | client | `delete_message` |
| DELETE | `/message` | client | `delete_all_messages` |
| GET | `/application` | client | `list_applications` |
| POST | `/application` | client | `create_application` |
| PUT | `/application/{id}` | client | `update_application` |
| DELETE | `/application/{id}` | client | `delete_application` |
| GET | `/client` | client | `list_clients` |
| POST | `/client` | client | `create_client` |
| DELETE | `/client/{id}` | client | `delete_client` |
| GET | `/health` | none | `health` |
| GET | `/version` | none | `version` |
| GET | `/current/user` | client | `current_user` |

## Client wrapper

`GotifyClient` in `gotify_mcp/services/gotify.py`:

| Concern | Implementation |
| --- | --- |
| Auth headers | `X-Gotify-Key` with per-request token selection |
| Base URL | Prefixed to all relative paths, normalized for Docker |
| Timeouts | 20s default for API calls, 10s for health/version |
| Error mapping | HTTP errors mapped to `{error, errorCode, errorDescription}` |
| Pagination | Client-side filtering and sorting for apps/clients; cursor-based (`since`) for messages |

## Docker URL normalization

When `is_docker()` returns true (detects `/.dockerenv` or `RUNNING_IN_DOCKER=true`), `localhost` and `127.0.0.1` in `GOTIFY_URL` are rewritten to `host.docker.internal`.

## Message extras

The `extras` field in `send_message` supports Gotify's extras specification:

| Key | Value | Effect |
| --- | --- | --- |
| `client::display.contentType` | `"text/markdown"` | Renders message body as Markdown in Gotify clients |
| `client::notification` | dict | Platform-specific notification overrides |

## API documentation

- Gotify API docs: `https://gotify.net/api-docs`
- Bundled API spec: `docs/gotify-api.json` (OpenAPI)

## Rate limiting

Gotify does not enforce rate limits at the API level. However, the MCP server truncates responses at 512 KB to prevent excessive context consumption.

## Testing

```bash
# Verify upstream is reachable
curl -sf "$GOTIFY_URL/health"

# Run live integration tests
just test-live
```

## Cross-references

- [ENV](../mcp/ENV.md) — all environment variables
- [ARCH](../stack/ARCH.md) — MCP server architecture and data flow
- [TOOLS](../mcp/TOOLS.md) — MCP tool definitions that wrap upstream endpoints
- [GUARDRAILS](../GUARDRAILS.md) — security rules for credential handling
