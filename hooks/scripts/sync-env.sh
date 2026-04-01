#!/usr/bin/env bash
set -euo pipefail

ENV_FILE="${CLAUDE_PLUGIN_ROOT}/.env"
BACKUP_DIR="${CLAUDE_PLUGIN_ROOT}/backups"
LOCK_FILE="${CLAUDE_PLUGIN_ROOT}/.env.lock"
mkdir -p "$BACKUP_DIR"

# Serialize concurrent sessions (two tabs starting at the same time)
exec 9>"$LOCK_FILE"
flock -w 10 9 || { echo "sync-env: failed to acquire lock after 10s" >&2; exit 1; }

declare -A MANAGED=(
  [GOTIFY_URL]="${CLAUDE_PLUGIN_OPTION_GOTIFY_URL:-}"
  [GOTIFY_APP_TOKEN]="${CLAUDE_PLUGIN_OPTION_GOTIFY_APP_TOKEN:-}"
  [GOTIFY_CLIENT_TOKEN]="${CLAUDE_PLUGIN_OPTION_GOTIFY_CLIENT_TOKEN:-}"
  [GOTIFY_MCP_URL]="${CLAUDE_PLUGIN_OPTION_GOTIFY_MCP_URL:-}"
  [GOTIFY_MCP_TOKEN]="${CLAUDE_PLUGIN_OPTION_GOTIFY_MCP_TOKEN:-}"
)

touch "$ENV_FILE"

# Backup before writing (max 3 retained)
if [ -s "$ENV_FILE" ]; then
  cp "$ENV_FILE" "${BACKUP_DIR}/.env.bak.$(date +%s)"
fi

# Write managed keys — awk handles arbitrary values safely (no delimiter injection)
for key in "${!MANAGED[@]}"; do
  value="${MANAGED[$key]}"
  [ -z "$value" ] && continue
  if grep -q "^${key}=" "$ENV_FILE" 2>/dev/null; then
    awk -v k="$key" -v v="$value" '$0 ~ "^"k"=" { print k"="v; next } { print }' \
      "$ENV_FILE" > "${ENV_FILE}.tmp" && mv "${ENV_FILE}.tmp" "$ENV_FILE"
  else
    echo "${key}=${value}" >> "$ENV_FILE"
  fi
done

# Fail if bearer token is not set — do NOT auto-generate.
# Auto-generated tokens cause a mismatch: the server reads the generated token
# but Claude Code sends the (empty) userConfig value. Every MCP call returns 401.
# Skip this check when auth is explicitly disabled via GOTIFY_MCP_NO_AUTH=true.
_no_auth=$(grep -E "^GOTIFY_MCP_NO_AUTH=" "$ENV_FILE" 2>/dev/null | cut -d= -f2 || true)
if [[ "$_no_auth" != "true" && "$_no_auth" != "1" ]]; then
  if ! grep -Eq "^GOTIFY_MCP_TOKEN=.+" "$ENV_FILE" 2>/dev/null; then
    echo "sync-env: ERROR — GOTIFY_MCP_TOKEN is not set." >&2
    echo "  Generate one:  openssl rand -hex 32" >&2
    echo "  Then paste it into the plugin's userConfig MCP token field." >&2
    echo "  Or set GOTIFY_MCP_NO_AUTH=true to disable auth (not recommended)." >&2
    exit 1
  fi
fi

chmod 600 "$ENV_FILE"

# Prune old backups (keep 3 most recent, chmod 600 on all)
mapfile -t baks < <(ls -t "${BACKUP_DIR}"/.env.bak.* 2>/dev/null)
for bak in "${baks[@]}"; do chmod 600 "$bak"; done
for bak in "${baks[@]:3}"; do rm -f "$bak"; done
