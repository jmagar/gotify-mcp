# Coding Rules — gotify-mcp

Standards and conventions enforced in the repository.

## Git workflow

### Conventional commits

| Prefix | Purpose | Example |
| --- | --- | --- |
| `feat:` | New feature | `feat: add list_clients action` |
| `fix:` | Bug fix | `fix: handle empty API response` |
| `chore:` | Maintenance | `chore: update dependencies` |
| `refactor:` | Code restructure | `refactor: extract client module` |
| `test:` | Tests | `test: add integration tests for send_message` |
| `docs:` | Documentation | `docs: update CONFIG reference` |
| `ci:` | CI/CD changes | `ci: add Docker security check` |

### Branch strategy

- `main` is production-ready at all times
- Feature branches for development
- PR required before merge to `main`

### Version tags

Tags use `vX.Y.Z` format. Created by the `just publish` recipe.

### Never commit

- `.env` files or any file containing credentials
- API keys, tokens, or passwords
- `__pycache__/`, `*.egg-info/`, `.cache/`

## Version bumping

### Bump type rules

| Commit prefix | Bump | Example |
| --- | --- | --- |
| `feat!:` or `BREAKING CHANGE` | Major | `0.3.1` -> `1.0.0` |
| `feat:` or `feat(...):` | Minor | `0.3.1` -> `0.4.0` |
| Everything else | Patch | `0.3.1` -> `0.3.2` |

### Version-bearing files

All must have the same version:

| File | Field |
| --- | --- |
| `pyproject.toml` | `version = "X.Y.Z"` |
| `.claude-plugin/plugin.json` | `"version": "X.Y.Z"` |
| `.codex-plugin/plugin.json` | `"version": "X.Y.Z"` |
| `gemini-extension.json` | `"version": "X.Y.Z"` |
| `CHANGELOG.md` | New entry under `## X.Y.Z` |

## Code standards

### Python

- Type hints on all function signatures
- Google-style docstrings
- f-strings for formatting
- `async`/`await` for I/O operations
- PEP 8 via `ruff format`
- Line length: 100 characters
- Target: Python 3.12

### Bash

```bash
#!/bin/bash
set -euo pipefail          # Strict mode
"$variable"                # Always quote variables
```

## Linting and formatting

| Tool | Command | Purpose |
| --- | --- | --- |
| `ruff check` | `just lint` | Lint: E, F, W, I, N, UP, B, A, SIM, TCH, RUF |
| `ruff format` | `just fmt` | Format |
| `ty check` | `just typecheck` | Type check |

## Security rules

See [GUARDRAILS](../GUARDRAILS.md). Key rules:

- Credentials in `.env` only
- `.env` has `chmod 600`
- Container runs as non-root
- No baked env vars in Docker image
- `/health` unauthenticated; all other endpoints require bearer auth
