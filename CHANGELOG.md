# Changelog

## [Unreleased]

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
