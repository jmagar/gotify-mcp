#!/usr/bin/env bash
set -euo pipefail

GITIGNORE="${CLAUDE_PLUGIN_ROOT}/.gitignore"

# Required patterns — credentials and backups must never be committed
REQUIRED=(
  ".env"
  ".env.*"
  "!.env.example"
)

touch "$GITIGNORE"

for pattern in "${REQUIRED[@]}"; do
  if ! grep -qxF "$pattern" "$GITIGNORE" 2>/dev/null; then
    echo "$pattern" >> "$GITIGNORE"
  fi
done
