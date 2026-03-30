FROM python:3.11-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

RUN groupadd --gid 1000 mcpuser && \
    useradd --uid 1000 --gid mcpuser --shell /bin/bash --create-home mcpuser

RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

COPY . .

RUN chmod +x entrypoint.sh && \
    mkdir -p /app/logs && \
    chown -R mcpuser:mcpuser /app

USER mcpuser

EXPOSE 9158

ENV GOTIFY_MCP_HOST=0.0.0.0
ENV GOTIFY_MCP_PORT=9158
ENV GOTIFY_MCP_TRANSPORT=http

HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:${GOTIFY_MCP_PORT:-9158}/health || exit 1

CMD ["./entrypoint.sh"]
