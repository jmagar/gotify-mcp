# Repository Structure — gotify-mcp

## Directory tree

```
gotify-mcp/
├── .claude-plugin/
│   └── plugin.json              # Claude Code plugin manifest
├── .codex-plugin/
│   └── plugin.json              # Codex plugin manifest
├── .github/
│   └── workflows/
│       ├── ci.yml               # Lint, typecheck, test, security
│       ├── docker-publish.yml   # Build + push Docker image
│       └── publish-pypi.yml     # Build + publish to PyPI + MCP Registry
├── docs/                        # Documentation (this tree)
├── gotify_mcp/                  # Server source code
│   ├── __init__.py
│   ├── server.py                # FastMCP server, action router, BearerAuth
│   └── services/
│       └── gotify.py            # Async HTTP client for Gotify REST API
├── hooks/
│   ├── hooks.json               # Hook declarations
│   └── scripts/
The `sync-uv.sh` hook keeps the repository lockfile and persistent Python environment in sync at session start.
│       ├──      # Enforce chmod 600 on .env

├── scripts/                     # Maintenance and CI scripts
│   ├── lint-plugin.sh




│   └── smoke-test.sh
├── skills/
│   └── gotify/
│       └── SKILL.md             # Skill definition
├── tests/
│   ├── test_live.sh             # Live integration smoke test
│   └── TEST_COVERAGE.md         # Coverage documentation
├── assets/                      # Plugin icons and logos
├── .env.example                 # Environment variable template
├── CHANGELOG.md                 # Version history
├── CLAUDE.md                    # Claude Code project instructions
├── Dockerfile                   # Multi-stage container build
├── Justfile                     # Task runner recipes
├── README.md                    # User-facing documentation
├── docker-compose.yml           # Docker Compose stack
├── entrypoint.sh                # Container entrypoint script
├── gemini-extension.json        # Gemini extension manifest
├── pyproject.toml               # Python project metadata and dependencies
├── server.json                  # MCP server registry entry
└── uv.lock                      # Dependency lock file
```

## Root files

| File | Required | Purpose |
| --- | --- | --- |
| `CLAUDE.md` | Yes | Project instructions for Claude Code sessions |
| `README.md` | Yes | User-facing overview, install, configuration, tool reference |
| `CHANGELOG.md` | Yes | Version history with entries for every bump |
| `.env.example` | Yes | Template for credentials — placeholder values only |
| `Justfile` | Yes | Task runner — dev, lint, test, docker, publish |
| `Dockerfile` | Yes | Multi-stage container build (builder + runtime) |
| `docker-compose.yml` | Yes | Orchestration with healthcheck and env |
| `entrypoint.sh` | Yes | Runtime env validation and startup |

## Plugin manifests

| File | Platform |
| --- | --- |
| `.claude-plugin/plugin.json` | Claude Code |
| `.codex-plugin/plugin.json` | Codex |
| `gemini-extension.json` | Gemini |
| `server.json` | MCP Registry |

All manifests have the same `version` value.

## Source code

| Directory | Entry point | Purpose |
| --- | --- | --- |
| `gotify_mcp/` | `gotify_mcp/server.py` | FastMCP server with action dispatch |
| `gotify_mcp/services/` | `gotify_mcp/services/gotify.py` | Async HTTP client for Gotify API |

## Plugin surfaces

| Directory | Surface |
| --- | --- |
| `skills/` | Skill definition (SKILL.md) |
| `hooks/` | Lifecycle hooks (session start, post-tool) |
