# Plugin Checklist — gotify-mcp

Pre-release and quality checklist. Complete all items before tagging a release.

## Version and metadata

- [ ] All version-bearing files in sync: `.claude-plugin/plugin.json`, `.codex-plugin/plugin.json`, `gemini-extension.json`, `pyproject.toml`
- [ ] `CHANGELOG.md` has an entry for the new version
- [ ] README version badge is correct

## Configuration

- [ ] `.env.example` documents every environment variable the server reads
- [ ] `.env.example` has no actual secrets — only placeholders
- [ ] `.env` is in `.gitignore` and `.dockerignore`

## Documentation

- [ ] `CLAUDE.md` is current and matches repo structure
- [ ] `README.md` has up-to-date tool reference and environment variable table
- [ ] `skills/gotify/SKILL.md` has correct frontmatter and action tables
- [ ] Setup instructions work from a clean clone

## Security

- [ ] No credentials in code, docs, or git history
- [ ] `.gitignore` includes `.env`, `*.secret`, credentials files
- [ ] `.dockerignore` includes `.env`, `.git/`, `*.secret`

- [ ] Destructive actions gated behind `confirm=True`
- [ ] `/health` endpoint is unauthenticated; all other endpoints require bearer auth
- [ ] Container runs as non-root (UID 1000)
- [ ] No baked environment variables in Docker image

## Build and test

- [ ] Docker image builds: `just build`
- [ ] Docker healthcheck passes: `just health`
- [ ] CI pipeline passes: lint, typecheck, test
- [ ] Live integration test passes: `just test-live`

## Deployment

- [ ] `docker-compose.yml` uses correct image tag and port (9158)
- [ ] `entrypoint.sh` is executable and validates required env vars
- [ ] SWAG/reverse-proxy config tested (if applicable)

## Registry (if publishing)

- [ ] `server.json` for MCP registry is valid with `tv.tootie/gotify-mcp` namespace
- [ ] Package published to PyPI (`gotify-mcp`)
- [ ] Docker image published to GHCR (`ghcr.io/jmagar/gotify-mcp`)
- [ ] DNS verification for `tv.tootie/gotify-mcp`

## Marketplace

- [ ] Entry in `claude-homelab` marketplace manifest
- [ ] Plugin installs correctly: `/plugin marketplace add jmagar/gotify-mcp`
