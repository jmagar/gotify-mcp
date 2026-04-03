# Gotify MCP Server

> **Streamlined notification management for Gotify via the Model Context Protocol.**

[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)](CHANGELOG.md)
[![Python Version](https://img.shields.io/badge/python-3.10+-green.svg)](https://www.python.org/downloads/)
[![FastMCP](https://img.shields.io/badge/FastMCP-Enabled-brightgreen.svg)](https://github.com/jlowin/fastmcp)
[![License](https://img.shields.io/badge/license-MIT-purple.svg)](LICENSE)

---

## ✨ Overview
Gotify MCP provides a unified toolset for interacting with your self-hosted Gotify instance. It enables AI assistants to send notifications, manage applications and clients, and monitor server health through a secure, local-first interface.

### 🎯 Key Features
| Feature | Description |
|---------|-------------|
| **Notification Engine** | Create messages with title, priority, and extras |
| **App Management** | Create, update, and rotate application tokens |
| **Client Control** | List and manage receiving clients |
| **User Context** | Built-in resource for current authenticated user info |

---

## 🎯 Claude Code Integration
The easiest way to use this plugin is through the Claude Code marketplace:

```bash
# Add the marketplace
/plugin marketplace add jmagar/claude-homelab

# Install the plugin
/plugin install gotify-mcp @jmagar-claude-homelab
```

---

## ⚙️ Configuration & Credentials
Credentials follow the standardized `homelab-core` pattern.

**Location:** `~/.claude-homelab/.env`

### Required Variables
```bash
GOTIFY_API_URL="https://gotify.example.com"
GOTIFY_CLIENT_TOKEN="YOUR_ADMIN_CLIENT_TOKEN"
GOTIFY_MCP_LOG_LEVEL="INFO"
```

> **Security Note:** Never commit `.env` files. Ensure permissions are set to `chmod 600`.

---

## 🛠️ Available Tools & Resources

### 🔧 Primary Tools
| Tool | Parameters | Description |
|------|------------|-------------|
| **`create_message`** | `app_token`, `message`, `priority` | Send a new notification |
| **`get_messages`** | `limit`, `since` | Retrieve recent message history |
| **`create_application`**| `name`, `description` | Manage sending applications |
| **`get_health`** | `none` | Monitor Gotify server status |

### 📊 Resources (`gotify://`)
| URI | Description | Output Format |
|-----|-------------|---------------|
| `gotify://currentuser` | Authenticated user details | JSON |
| `gotify://application/{id}/messages`| Application-specific message feed | List |

---

## 🏗️ Architecture & Design
This server implements the core Gotify API using an async `httpx` engine:
- **Shared Request Helper:** Centralized error handling and authentication parsing.
- **FastMCP SSE/HTTP:** Configurable transport for diverse MCP client requirements.
- **Resource Routing:** Direct mapping to user and application message feeds.

---

## 🔧 Development
### Prerequisites
- Python 3.10+
- [uv](https://github.com/astral-sh/uv) package manager

### Setup
```bash
uv sync
uv run python gotify_mcp_server.py
```

### Transport Options
```bash
# Set transport via env var
GOTIFY_MCP_TRANSPORT="http" # 'http', 'sse', or 'stdio'
```

---

## 🐛 Troubleshooting
| Issue | Cause | Solution |
|-------|-------|----------|
| **401 Unauthorized** | Token Mismatch | Verify `GOTIFY_CLIENT_TOKEN` |
| **Connection Refused**| Bind Address | Check `GOTIFY_MCP_HOST` / `PORT` |
| **Failed Messages** | Invalid App Token | Use correct token for `create_message` |

---

## 📄 License
MIT © jmagar
