# syntax=docker/dockerfile:1

# ── builder ──────────────────────────────────────────────────────────────────
FROM python:3.12-slim AS builder

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Install dependencies first (layer cache)
COPY pyproject.toml uv.lock README.md ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --no-install-project

# Copy source and install project
COPY gotify_mcp/ ./gotify_mcp/
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

# ── runtime ──────────────────────────────────────────────────────────────────
FROM python:3.12-slim AS runtime

RUN groupadd --gid 1000 mcpuser && \
    useradd --uid 1000 --gid mcpuser --shell /bin/bash --create-home mcpuser

WORKDIR /app

# Copy the built venv and source from builder
COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app/gotify_mcp /app/gotify_mcp
COPY --from=builder /app/pyproject.toml /app/pyproject.toml
COPY --from=builder /app/README.md /app/README.md

# Copy entrypoint and set up log directory
COPY entrypoint.sh ./
RUN chmod +x entrypoint.sh && \
    mkdir -p /app/logs && \
    chown -R 1000:1000 /app

USER 1000:1000

EXPOSE 9158

ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    GOTIFY_MCP_HOST=0.0.0.0 \
    GOTIFY_MCP_PORT=9158 \
    GOTIFY_MCP_TRANSPORT=http

HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD python -c "import os, sys, urllib.request; port = os.environ.get('GOTIFY_MCP_PORT', '9158'); \
url = f'http://localhost:{port}/health'; \
resp = urllib.request.urlopen(url, timeout=5); sys.exit(0 if resp.status == 200 else 1)"

CMD ["./entrypoint.sh"]
