# ==========================================
# 1. Builder stage (Construcción con uv)
# ==========================================
FROM python:3.12-slim AS builder
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project --no-dev

COPY main.py ./main.py
COPY src ./src
COPY alembic.ini ./alembic.ini
COPY alembic ./alembic
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

# ==========================================
# 2. Stage final (imagen liviana)
# ==========================================
FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/app/.venv/bin:$PATH" \
    PYTHONPATH=/app

WORKDIR /app

RUN addgroup --system appgroup && adduser --system --group appuser

COPY --from=builder --chown=appuser:appgroup /app/.venv /app/.venv
COPY --chown=appuser:appgroup main.py ./main.py
COPY --chown=appuser:appgroup src ./src
COPY --chown=appuser:appgroup alembic.ini ./alembic.ini
COPY --chown=appuser:appgroup alembic ./alembic
COPY --chown=appuser:appgroup entrypoint.sh ./entrypoint.sh

USER appuser

EXPOSE 8000

ENTRYPOINT ["sh", "./entrypoint.sh"]