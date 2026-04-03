dev:
    uv run python -m gotify_mcp.server

lint:
    uv run ruff check .

fmt:
    uv run ruff format .

typecheck:
    uv run ty check

test:
    uv run pytest

build:
    docker build -t gotify-mcp .

up:
    docker compose up -d

down:
    docker compose down

restart:
    docker compose restart

logs:
    docker compose logs -f

health:
    curl -sf http://localhost:9158/health | jq .

test-live:
    bash tests/test_live.sh

setup:
    cp -n .env.example .env || true
    uv sync --all-extras --dev

gen-token:
    openssl rand -hex 32

check-contract:
    bash scripts/lint-plugin.sh

validate-skills:
    @test -f skills/gotify/SKILL.md && echo "OK" || echo "MISSING: skills/gotify/SKILL.md"

clean:
    rm -rf dist/ .cache/ *.egg-info/
    find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true

# Publish: bump version, tag, push (triggers PyPI + Docker publish)
publish bump="patch":
    #!/usr/bin/env bash
    set -euo pipefail
    [ "$(git branch --show-current)" = "main" ] || { echo "Switch to main first"; exit 1; }
    [ -z "$(git status --porcelain)" ] || { echo "Commit or stash changes first"; exit 1; }
    git pull origin main
    CURRENT=$(grep -m1 "^version" pyproject.toml | sed "s/.*\"\(.*\)\".*/\1/")
    IFS="." read -r major minor patch <<< "$CURRENT"
    case "{{bump}}" in
      major) major=$((major+1)); minor=0; patch=0 ;;
      minor) minor=$((minor+1)); patch=0 ;;
      patch) patch=$((patch+1)) ;;
      *) echo "Usage: just publish [major|minor|patch]"; exit 1 ;;
    esac
    NEW="${major}.${minor}.${patch}"
    echo "Version: ${CURRENT} → ${NEW}"
    sed -i "s/^version = \"${CURRENT}\"/version = \"${NEW}\"/" pyproject.toml
    for f in .claude-plugin/plugin.json .codex-plugin/plugin.json gemini-extension.json; do
      [ -f "$f" ] && python3 -c "import json; d=json.load(open(\"$f\")); d[\"version\"]=\"${NEW}\"; json.dump(d,open(\"$f\",\"w\"),indent=2); open(\"$f\",\"a\").write(\"
\")"
    done
    git add -A && git commit -m "release: v${NEW}" && git tag "v${NEW}" && git push origin main --tags
    echo "Tagged v${NEW} — publish workflow will run automatically"

