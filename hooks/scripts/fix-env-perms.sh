#!/usr/bin/env bash
set -euo pipefail

ENV_FILE="${CLAUDE_PLUGIN_ROOT}/.env"

# Nothing to do if .env doesn't exist
[ -f "$ENV_FILE" ] || exit 0

# Read tool event from stdin
input=$(cat)
tool_name=$(echo "$input" | jq -r '.tool_name // ""')
tool_input=$(echo "$input" | jq -r '.tool_input // {}')

touched_env=false

case "$tool_name" in
  Write|Edit|MultiEdit)
    file_path=$(echo "$tool_input" | jq -r '.file_path // ""')
    [[ "$file_path" == *".env"* ]] && touched_env=true
    ;;
  Bash)
    command=$(echo "$tool_input" | jq -r '.command // ""')
    [[ "$command" == *".env"* ]] && touched_env=true
    ;;
esac

if [ "$touched_env" = true ]; then
  chmod 600 "$ENV_FILE"
  # Also secure any backups created mid-session
  for bak in "${CLAUDE_PLUGIN_ROOT}"/.env.bak.*; do
    [ -f "$bak" ] && chmod 600 "$bak"
  done
fi
