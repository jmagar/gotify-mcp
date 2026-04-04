# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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
- ensure-ignore-files.sh hook for .gitignore and .dockerignore
- .codex-plugin/plugin.json and .app.json for Codex CLI support
- assets/ directory with icon and logo placeholders
- gotify_mcp_token userConfig entry in plugin.json
- .dockerignore with all required patterns
- flock-based concurrency in sync-env.sh
- awk-based env replacement in sync-env.sh

## [0.1.0] - 2026-03-29

### Added
- Initial release
- Gotify message sending, listing, deleting
- Gotify application and client management
- Docker Compose deployment
