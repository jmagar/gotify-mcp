dev:
    uv run python -m gotify_mcp

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
