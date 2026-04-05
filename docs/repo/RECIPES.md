# Justfile Recipes — gotify-mcp

Standard task runner recipes. Run `just --list` to see all available recipes.

## Development

| Recipe | Command | Purpose |
| --- | --- | --- |
| `dev` | `uv run python -m gotify_mcp.server` | Run dev server |
| `lint` | `uv run ruff check .` | Run linter |
| `fmt` | `uv run ruff format .` | Format code |
| `typecheck` | `uv run ty check` | Type checking |
| `test` | `uv run pytest` | Run unit tests |
| `test-live` | `bash tests/test_live.sh` | Run live integration tests |

## Docker

| Recipe | Command | Purpose |
| --- | --- | --- |
| `build` | `docker build -t gotify-mcp .` | Build Docker image |
| `up` | `docker compose up -d` | Start via Docker Compose |
| `down` | `docker compose down` | Stop containers |
| `restart` | `docker compose restart` | Restart containers |
| `logs` | `docker compose logs -f` | Tail container logs |

## Health and status

| Recipe | Command | Purpose |
| --- | --- | --- |
| `health` | `curl -sf http://localhost:9158/health \| jq .` | Check server health |
| `gen-token` | `openssl rand -hex 32` | Generate a bearer token |

## Setup

| Recipe | Command | Purpose |
| --- | --- | --- |
| `setup` | `cp -n .env.example .env; uv sync --all-extras --dev` | Initial setup |

## Quality

| Recipe | Command | Purpose |
| --- | --- | --- |
| `check-contract` | `bash scripts/lint-plugin.sh` | Validate plugin manifests |
| `validate-skills` | Check for `skills/gotify/SKILL.md` | Validate skill files exist |
| `clean` | `rm -rf dist/ .cache/ *.egg-info/; find . -name __pycache__ -exec rm -rf {} +` | Remove build artifacts |

## Publishing

| Recipe | Command | Purpose |
| --- | --- | --- |
| `publish [bump]` | Version bump, tag, push | Release to PyPI and GHCR |

The `publish` recipe:

1. Verifies on `main` branch with clean working tree
2. Pulls latest from origin
3. Reads current version from `pyproject.toml`
4. Bumps version in `pyproject.toml`, `.claude-plugin/plugin.json`, `.codex-plugin/plugin.json`, `gemini-extension.json`
5. Commits as `release: vX.Y.Z`
6. Tags `vX.Y.Z`
7. Pushes to origin (triggers CI publish workflows)

Bump types: `major`, `minor`, `patch` (default: `patch`).
