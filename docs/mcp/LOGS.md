# Logging and Error Handling

Logging and error handling patterns for `gotify-mcp`.

## Log Configuration

| Env Var | Values | Default |
|---------|--------|---------|
| `GOTIFY_LOG_LEVEL` | `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL` | `INFO` |

Also accepts the generic `LOG_LEVEL` as a fallback if `GOTIFY_LOG_LEVEL` is not set.

## Implementation

The server uses Python's `logging` module with two handlers:

```python
# Console handler — stdout
logging.StreamHandler(sys.stdout)
# Format: 2026-04-04 12:00:00 - GotifyMCPServer - INFO - message

# File handler — rotating
logging.handlers.RotatingFileHandler(
    "logs/gotify_mcp.log",
    maxBytes=5 * 1024 * 1024,  # 5 MB
    backupCount=3,
)
# Format: timestamp - name - level - module - function - line - message
```

## Log Location

| Context | Path |
|---------|------|
| Local dev | `./logs/gotify_mcp.log` |
| Docker | `/app/logs/gotify_mcp.log` (named volume `gotify-mcp-logs`) |

Access Docker logs:

```bash
just logs            # Tails compose logs (stdout)
docker compose logs -f gotify-mcp
```

## Error Handling

### Consistent Error Response

All errors return a JSON string with three fields:

```json
{
  "error": "Unauthorized",
  "errorCode": 401,
  "errorDescription": "Authentication token missing."
}
```

### Common Errors

| error | errorCode | Cause |
| --- | --- | --- |
| `Unauthorized` | 401 | Wrong or missing token type for the operation |
| `HTTP 403` | 403 | Token valid but operation not permitted |
| `HTTP 404` | 404 | Message, application, or client ID does not exist |
| `NoUpdateFields` | 400 | `update_application` called with no fields to update |
| `RequestError` | 500 | Network failure reaching the Gotify server |
| `No token provided` | 401 | Neither `app_token` nor `GOTIFY_CLIENT_TOKEN` is set |

### Timeout Protection

Default 20s timeout for upstream calls via `httpx.AsyncClient`. Health and version checks use a 10s timeout.

### Response Truncation

Responses are capped at 512 KB. Truncated responses include `... [truncated]` at the end.

### Credential Safety

- Token presence is logged as `SET` or `NOT SET` in the startup banner
- Never log the actual token values
- Redact `X-Gotify-Key` headers in debug output

## Related Docs

- [DEPLOY.md](DEPLOY.md) — Docker volume mounts for logs
- [ENV.md](ENV.md) — `GOTIFY_LOG_LEVEL` and other env vars
- [TESTS.md](TESTS.md) — testing error conditions
