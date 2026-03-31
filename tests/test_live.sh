#!/usr/bin/env bash
set -euo pipefail
TOKEN="${GOTIFY_MCP_TOKEN:?GOTIFY_MCP_TOKEN must be set}"
BASE_URL="${GOTIFY_MCP_URL:-http://localhost:8084}"

echo "Testing unauthenticated rejection..."
status=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/mcp")
[ "$status" = "401" ] || { echo "FAIL: expected 401, got $status"; exit 1; }

echo "Testing bad token rejection..."
status=$(curl -s -o /dev/null -w "%{http_code}" -H "Authorization: Bearer bad-token" "$BASE_URL/mcp")
[ "$status" = "401" ] || { echo "FAIL: expected 401 for bad token, got $status"; exit 1; }

echo "Testing health..."
timeout 30 curl -sf "$BASE_URL/health" | jq .

echo "All live tests passed."
