#!/bin/bash

set -e # Exit immediately if a command exits with a non-zero status.

echo "Gotify MCP Service: Initializing..."

# Validate required environment variables
if [ -z "$GOTIFY_URL" ]; then
    echo "Error: GOTIFY_URL environment variable is required"
    exit 1
fi

if [ -z "$GOTIFY_CLIENT_TOKEN" ]; then
    echo "Warning: GOTIFY_CLIENT_TOKEN is not set. Some functionality may be limited."
fi

# Set defaults for MCP server configuration
export GOTIFY_MCP_HOST=${GOTIFY_MCP_HOST:-"0.0.0.0"}
export GOTIFY_MCP_PORT=${GOTIFY_MCP_PORT:-"9158"}
export GOTIFY_MCP_TRANSPORT=${GOTIFY_MCP_TRANSPORT:-"http"}
export GOTIFY_LOG_LEVEL=${GOTIFY_LOG_LEVEL:-"INFO"}

echo "Gotify MCP Service: Configuration validated"
echo "  - GOTIFY_URL: $GOTIFY_URL"
echo "  - GOTIFY_CLIENT_TOKEN: $([ -n "$GOTIFY_CLIENT_TOKEN" ] && echo "***SET***" || echo "NOT SET")"
echo "  - GOTIFY_APP_TOKEN: $([ -n "$GOTIFY_APP_TOKEN" ] && echo "***SET***" || echo "NOT SET")"
echo "  - MCP_HOST: $GOTIFY_MCP_HOST"
echo "  - MCP_PORT: $GOTIFY_MCP_PORT"
echo "  - MCP_TRANSPORT: $GOTIFY_MCP_TRANSPORT"
echo "  - LOG_LEVEL: $GOTIFY_LOG_LEVEL"

# Change to app directory (important for relative path handling)
cd /app

echo "Gotify MCP Service: Starting server..."
exec python3 gotify-mcp-server.py 