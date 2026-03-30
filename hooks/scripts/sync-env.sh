#!/usr/bin/env bash
set -euo pipefail

ENV_FILE="${CLAUDE_PLUGIN_ROOT}/.env"

# Credentials from userConfig, exported automatically as CLAUDE_PLUGIN_OPTION_* vars
declare -A MANAGED=(
  [GOTIFY_URL]="${CLAUDE_PLUGIN_OPTION_GOTIFY_URL:-}"
  [GOTIFY_APP_TOKEN]="${CLAUDE_PLUGIN_OPTION_GOTIFY_APP_TOKEN:-}"
  [GOTIFY_CLIENT_TOKEN]="${CLAUDE_PLUGIN_OPTION_GOTIFY_CLIENT_TOKEN:-}"
  [GOTIFY_MCP_URL]="${CLAUDE_PLUGIN_OPTION_GOTIFY_MCP_URL:-}"
)

# Create .env if it doesn't exist
touch "$ENV_FILE"

# Update existing line or append — skip empty values to avoid clobbering
for key in "${!MANAGED[@]}"; do
  value="${MANAGED[$key]}"
  [ -z "$value" ] && continue
  if grep -q "^${key}=" "$ENV_FILE" 2>/dev/null; then
    sed -i "s|^${key}=.*|${key}=${value}|" "$ENV_FILE"
  else
    echo "${key}=${value}" >> "$ENV_FILE"
  fi
done

# Always enforce restrictive permissions — credentials must not be world-readable
chmod 600 "$ENV_FILE"

# Lock down backup files and prune to keep only the 3 most recent
mapfile -t baks < <(ls -t "${CLAUDE_PLUGIN_ROOT}"/.env.bak.* 2>/dev/null)
for bak in "${baks[@]}"; do
  chmod 600 "$bak"
done
# Delete oldest beyond the 3-backup limit
for bak in "${baks[@]:3}"; do
  rm -f "$bak"
done
