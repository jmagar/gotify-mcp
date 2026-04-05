# Prerequisites — gotify-mcp

Required tools and versions before developing or deploying.

## Required tools

| Tool | Version | Install | Purpose |
| --- | --- | --- | --- |
| Python | 3.12+ | System or pyenv | Runtime |
| uv | latest | `curl -LsSf https://astral.sh/uv/install.sh \| sh` | Package manager |
| Git | 2.40+ | System package manager | Version control |
| Docker | 24+ | [docs.docker.com](https://docs.docker.com/get-docker/) | Container builds |
| Docker Compose | v2+ | Bundled with Docker Desktop | Service orchestration |
| just | latest | `cargo install just` | Task runner |
| openssl | any | System package manager | Token generation |
| curl | any | System package manager | HTTP testing |
| jq | 1.6+ | System package manager | JSON parsing |

### Verify

```bash
python3 --version        # Python 3.12.x
uv --version             # uv X.Y.Z
git --version            # git version 2.40+
docker --version         # Docker version 24+
docker compose version   # Docker Compose version v2+
just --version           # just X.Y.Z
openssl version          # OpenSSL X.Y.Z
```

## External service

A running **Gotify server** is required for full functionality:

| Requirement | How to obtain |
| --- | --- |
| Gotify server URL | Deploy Gotify (Docker, binary, or hosted) |
| App token | Gotify UI: Settings > Apps > Create Application |
| Client token | Gotify UI: Settings > Clients > Create Client |

Without a Gotify server, only the health endpoint and help tool work.

## Quick start

```bash
git clone https://github.com/jmagar/gotify-mcp.git
cd gotify-mcp
just setup           # Copy .env.example -> .env, install deps
# Edit .env with your Gotify credentials
just dev             # Start dev server on port 9158
```

## Optional tools

| Tool | Purpose | Install |
| --- | --- | --- |
| `gh` | GitHub CLI for PRs and releases | [cli.github.com](https://cli.github.com/) |
| `docker scout` | Container vulnerability scanning | Bundled with Docker Desktop |

## Cross-references

- [SETUP](../SETUP.md) — step-by-step setup guide
- [TECH](TECH.md) — technology stack details
- [RECIPES](../repo/RECIPES.md) — Justfile recipes for development
