#!/bin/bash
set -euo pipefail

echo "Gotify MCP Service: Initializing..."

# Required service URL
if [ -z "${GOTIFY_URL:-}" ]; then
    echo "Error: GOTIFY_URL environment variable is required" >&2
    exit 1
fi

# Bearer token required for HTTP transport (unless NO_AUTH disabled)
GOTIFY_MCP_TRANSPORT=${GOTIFY_MCP_TRANSPORT:-"http"}
GOTIFY_MCP_NO_AUTH=${GOTIFY_MCP_NO_AUTH:-"false"}
if [ "$GOTIFY_MCP_TRANSPORT" != "stdio" ] && [ "$GOTIFY_MCP_NO_AUTH" != "true" ]; then
    if [ -z "${GOTIFY_MCP_TOKEN:-}" ]; then
        echo "Error: GOTIFY_MCP_TOKEN must be set for HTTP transport." >&2
        echo "Generate with: openssl rand -hex 32" >&2
        echo "Or set GOTIFY_MCP_NO_AUTH=true to disable bearer auth." >&2
        exit 1
    fi
fi

if [ -z "${GOTIFY_CLIENT_TOKEN:-}" ]; then
    echo "Warning: GOTIFY_CLIENT_TOKEN is not set. Management actions will fail."
fi

export GOTIFY_MCP_HOST=${GOTIFY_MCP_HOST:-"0.0.0.0"}
export GOTIFY_MCP_PORT=${GOTIFY_MCP_PORT:-"9158"}
export GOTIFY_MCP_TRANSPORT
export GOTIFY_LOG_LEVEL=${GOTIFY_LOG_LEVEL:-"INFO"}

echo "Gotify MCP Service: Configuration validated"
echo "  - GOTIFY_URL: $GOTIFY_URL"
echo "  - GOTIFY_CLIENT_TOKEN: $([ -n "${GOTIFY_CLIENT_TOKEN:-}" ] && echo "SET" || echo "NOT SET")"
echo "  - GOTIFY_MCP_TOKEN: $([ -n "${GOTIFY_MCP_TOKEN:-}" ] && echo "SET" || echo "NOT SET")"
echo "  - MCP_HOST: $GOTIFY_MCP_HOST"
echo "  - MCP_PORT: $GOTIFY_MCP_PORT"
echo "  - MCP_TRANSPORT: $GOTIFY_MCP_TRANSPORT"
echo "  - LOG_LEVEL: $GOTIFY_LOG_LEVEL"

echo "Gotify MCP Service: Starting server..."
exec python -m gotify_mcp.server
