# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.3.3] - 2026-04-15

### Changed
- Repository maintenance updates committed from the current working tree.
- Version-bearing manifests synchronized to 0.3.3.


## [0.3.2] - 2026-04-04

### Added
- Full documentation structure with references, troubleshooting, and quick-reference guides
- `tests/TEST_COVERAGE.md` documenting test coverage status

## [0.3.1] - 2026-04-04

### Security
- **CVE-2026-32871** (CRITICAL): upgrade `fastmcp` to `>=3.2.0` — fixes SSRF & Path Traversal in OpenAPI provider
- **CVE-2026-27124** (HIGH): upgrade `fastmcp` to `>=3.2.0` — fixes missing consent verification in OAuth proxy callback
- Add `ignore-unfixed: true` to Trivy scan — suppresses OS-level CVEs with no upstream fix available

## [0.3.0] - 2026-04-04

### Added
- **MCP Registry publishing**: `server.json` conforming to the official MCP Registry schema; published as `tv.tootie/gotify-mcp`
- **Automated registry CI**: `publish-pypi.yml` extended to authenticate via DNS (tootie.tv Ed25519 key) and publish to `registry.modelcontextprotocol.io` after each PyPI release
- **PyPI ownership verification**: `<!-- mcp-name: tv.tootie/gotify-mcp -->` comment in README for registry validation
- **OCI discoverability label**: `io.modelcontextprotocol.server.name` LABEL added to Dockerfile

## [0.2.2] - 2026-04-03

### Fixed
- **OAuth discovery 401 cascade**: BearerAuthMiddleware was blocking GET /.well-known/oauth-protected-resource, causing MCP clients to surface generic "unknown error". Added WellKnownMiddleware (RFC 9728) to return resource metadata.

### Added
- **docs/AUTHENTICATION.md**: New setup guide covering token generation and client config.
- **README Authentication section**: Added quick-start examples and link to full guide.



### Added
- FastMCP server with `gotify` and `gotify_help` tools
- BearerAuthMiddleware with startup token validation
- Dual transport (http/stdio via GOTIFY_MCP_TRANSPORT)
- Action+subaction pattern for all Gotify operations
- CLAUDE.md, AGENTS.md, GEMINI.md AI memory files
- Multi-stage Dockerfile with non-root user (1000:1000)

- .codex-plugin/plugin.json and .app.json for Codex CLI support
- assets/ directory with icon and logo placeholders
- gotify_mcp_token userConfig entry in plugin.json
- .dockerignore with all required patterns
- flock-based concurrency in sync-uv.sh
- awk-based env replacement in sync-uv.sh

## [0.1.0] - 2026-03-29

### Added
- Initial release
- Gotify message sending, listing, deleting
- Gotify application and client management
- Docker Compose deployment
