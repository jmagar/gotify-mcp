# CI/CD Workflows

GitHub Actions configuration for `gotify-mcp`.

## Workflows

### ci.yml — Continuous Integration

Runs on every push to `main` and on pull requests.

| Job | Steps |
| --- | --- |
| `lint` | `uv sync --group dev` then `ruff check .` and `ruff format --check .` |
| `typecheck` | `uv sync --group dev` then `ty check` |
| `test` | `uv sync --group dev` then `pytest` |
| `audit` | `uv export --no-hashes \| uv pip compile - -q \| uv pip audit --stdin` |
| `contract-drift` | `bash scripts/lint-plugin.sh` |
| `docker-security` | `check-docker-security.sh`, `check-no-baked-env.sh`, `ensure-ignore-files.sh` |
| `mcp-integration` | Runs `tests/test_live.sh --mode docker` with live Gotify credentials (main push only) |

### docker-publish.yml — Container Images

Triggered on push to `main`, version tags, and pull requests.

- Builds multi-arch images (`linux/amd64`, `linux/arm64`) via Docker Buildx
- Pushes to `ghcr.io/jmagar/gotify-mcp` (skipped for PRs)
- Tags: branch name, semver components, `latest` for default branch, SHA
- Runs Trivy vulnerability scan on pushed images
- Generates SBOM and provenance attestations

### publish-pypi.yml — Package Publishing

Triggered on tag push (`v*.*.*`).

1. Verifies tag version matches `pyproject.toml` version
2. Builds package with `uv build`
3. Publishes to PyPI via trusted publishing (OIDC, no stored token)
4. Creates GitHub Release with generated notes and dist artifacts
5. Authenticates to MCP Registry via DNS (`tootie.tv` domain)
6. Publishes `server.json` to MCP Registry under `tv.tootie/gotify-mcp`

## Secrets Required

| Secret | Purpose | How to Set |
|--------|---------|------------|
| `GITHUB_TOKEN` | Auto-provided | Built-in |
| `GOTIFY_URL` | Upstream URL for live tests | Repo settings > Secrets |
| `GOTIFY_APP_TOKEN` | App token for live tests | Repo settings > Secrets |
| `GOTIFY_CLIENT_TOKEN` | Client token for live tests | Repo settings > Secrets |
| `MCP_PRIVATE_KEY` | DNS auth for MCP Registry publish | Repo settings > Secrets |

MCP bearer tokens are generated at CI runtime and do not need to be stored as secrets.

## Related Docs

- [TESTS.md](TESTS.md) — test commands referenced by CI
- [MCPORTER.md](MCPORTER.md) — live smoke tests in CI
- [PUBLISH.md](PUBLISH.md) — versioning and release workflow
- [PRE-COMMIT.md](PRE-COMMIT.md) — hooks that CI also enforces
