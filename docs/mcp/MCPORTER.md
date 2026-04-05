# Live Smoke Testing

End-to-end verification against a running `gotify-mcp` server. Complements unit tests in [TESTS.md](TESTS.md).

## Purpose

`tests/test_live.sh` exercises the full MCP server stack: auth, tool dispatch, and error handling against a real Gotify server.

## Location

```
tests/test_live.sh
```

## Modes

| Mode | Command | Description |
|------|---------|-------------|
| `http` | `bash tests/test_live.sh` | Tests against HTTP transport (default) |
| `docker` | `bash tests/test_live.sh --mode docker` | Starts container, tests, tears down |

Shortcut: `just test-live`

## Test Coverage

The live test script covers:

1. Health endpoint accessibility (no auth)
2. Bearer token rejection with invalid token
3. Sending messages via app token
4. Listing messages
5. Listing applications
6. Creating and deleting applications
7. Server version and health via tool calls
8. Error handling for invalid actions

## Environment

Required env vars (from `.env` or CI secrets):

| Variable | Purpose |
|----------|---------|
| `GOTIFY_URL` | Upstream Gotify server URL |
| `GOTIFY_APP_TOKEN` | App token for sending test messages |
| `GOTIFY_CLIENT_TOKEN` | Client token for management operations |
| `GOTIFY_MCP_TOKEN` | MCP Bearer token |
| `GOTIFY_MCP_PORT` | Server port (defaults to `9158`) |

## CI Integration

Live tests run on `main` push only (requires secrets). Skipped on PRs from forks.

```yaml
mcp-integration:
  needs: [lint, typecheck, test]
  if: github.event_name == 'push' || github.event.pull_request.head.repo.full_name == github.repository
  steps:
    - uses: actions/checkout@v4
    - uses: astral-sh/setup-uv@v5
    - name: Run integration tests
      env:
        GOTIFY_URL: ${{ secrets.GOTIFY_URL }}
        GOTIFY_APP_TOKEN: ${{ secrets.GOTIFY_APP_TOKEN }}
        GOTIFY_CLIENT_TOKEN: ${{ secrets.GOTIFY_CLIENT_TOKEN }}
      run: bash tests/test_live.sh --mode docker
```

## Running Locally

```bash
# Start server in background
just dev &

# Run smoke tests
just test-live

# Or directly
bash tests/test_live.sh
```

## Related Docs

- [TESTS.md](TESTS.md) — unit tests
- [CICD.md](CICD.md) — CI workflow that runs these tests
- [AUTH.md](AUTH.md) — authentication details
