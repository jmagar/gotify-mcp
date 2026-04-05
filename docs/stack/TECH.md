# Technology Choices — gotify-mcp

## Language and runtime

| Component | Choice | Version |
| --- | --- | --- |
| Language | Python | 3.12+ |
| Package manager | uv | latest |
| MCP framework | FastMCP | >=3.2.0 |
| HTTP client | httpx | >=0.28.1 |
| Env loading | python-dotenv | >=1.1.0 |

## Why these choices

### FastMCP

FastMCP wraps the low-level MCP protocol and provides:
- `@mcp.tool()` decorator for tool registration
- `@mcp.custom_route()` for custom HTTP endpoints (e.g., `/health`)
- Automatic JSON Schema generation from Python type annotations
- Built-in stdio and streamable-HTTP transport
- Starlette-based middleware support for authentication

### httpx

Async HTTP client with:
- Connection pooling
- Configurable timeouts (20s for API calls, 10s for health checks)
- `raise_for_status()` for clean error handling
- No external dependency on `requests`

### uv

Fast Python package manager that replaces pip, pip-tools, and virtualenv:
- `uv sync` for deterministic installs from `uv.lock`
- `uv run` for running in the project venv
- `uv build` for package building
- Used in CI via `astral-sh/setup-uv@v5`

## Linting and formatting

| Tool | Command | Purpose |
| --- | --- | --- |
| ruff check | `just lint` | Linting: E, F, W, I, N, UP, B, A, SIM, TCH, RUF rules |
| ruff format | `just fmt` | Code formatting (PEP 8, 100 char line length) |
| ty | `just typecheck` | Type checking |

## Testing

| Framework | Command | Purpose |
| --- | --- | --- |
| pytest | `just test` | Unit tests |
| pytest-asyncio | — | Async test support |
| test_live.sh | `just test-live` | Shell-based live integration tests |

## Docker

Multi-stage build:

| Stage | Base image | Purpose |
| --- | --- | --- |
| builder | `python:3.12-slim` + `ghcr.io/astral-sh/uv:0.10.10` | Install deps, build project |
| runtime | `python:3.12-slim` | Minimal runtime with venv only |

Container conventions:
- Non-root user (UID 1000, `mcpuser`)
- Healthcheck via Python `urllib.request`
- No baked credentials
- `entrypoint.sh` for runtime env validation

## Dependency management

| File | Purpose |
| --- | --- |
| `pyproject.toml` | Project metadata, dependencies, tool config |
| `uv.lock` | Deterministic dependency lock |

Add a dependency:
```bash
uv add <package>
```

Update all:
```bash
uv lock --upgrade
```

## Cross-references

- [ARCH](ARCH.md) — architecture patterns
- [PRE-REQS](PRE-REQS.md) — prerequisites for development
- [RECIPES](../repo/RECIPES.md) — Justfile recipes
