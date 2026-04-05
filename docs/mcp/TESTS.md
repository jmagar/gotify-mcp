# Testing Guide

Testing patterns for `gotify-mcp`. All non-live testing is covered here; see [MCPORTER.md](MCPORTER.md) for end-to-end smoke tests.

## Unit Tests

```bash
uv run pytest tests/ -v
```

Shortcut: `just test`

Tests live in `tests/`. Use `pytest-asyncio` for async test functions.

## Integration Tests

Integration tests hit a real Gotify server and require credentials.

| Concern | Pattern |
|---------|---------|
| Credentials | `.env` locally, GitHub secrets in CI |
| CI behavior | Runs on `main` push only, skipped on PRs from forks |
| Command | `bash tests/test_live.sh` |

```bash
# Run integration tests locally
just test-live
```

## Test Structure

```
tests/
  test_live.sh           # Shell-based live integration tests
  TEST_COVERAGE.md       # Documents what is and isn't tested
```

## Testing Checklist

- [ ] Tool dispatch — every action returns expected shape
- [ ] Auth: valid token — 200 with correct Bearer token
- [ ] Auth: invalid token — 401
- [ ] Auth: no token — 401 (or 200 if `GOTIFY_MCP_NO_AUTH=true`)
- [ ] Health endpoint — `GET /health` returns 200 with no auth
- [ ] Error conditions — upstream timeout, 404, 500 propagate correctly
- [ ] Destructive operation gates — delete actions require `confirm=True`
- [ ] Token type enforcement — app token for send_message, client token for management

## CI Configuration

Tests run automatically in CI. See [CICD.md](CICD.md) for workflow details.

```yaml
test:
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v4
    - uses: astral-sh/setup-uv@v5
    - run: uv sync --group dev
    - run: uv run pytest
```

## Related Docs

- [MCPORTER.md](MCPORTER.md) — live smoke tests
- [CICD.md](CICD.md) — CI workflow configuration
- [LOGS.md](LOGS.md) — error handling patterns tested here
