# ==========================================
# 1. Builder stage (Construcción con uv)
# ==========================================
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS builder

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project --no-dev

COPY . /app
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

# ==========================================
# 2. Stage Final (Imagen liviana para producción)
# ==========================================
FROM python:3.12-slim

# Evitar .pyc en runtime, asegurar logs inmediatos y agregar el venv al PATH
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/app/.venv/bin:$PATH"

WORKDIR /app

# Crear un usuario y grupo sin privilegios por seguridad
RUN addgroup --system appgroup && adduser --system --group appuser

# Copiar el entorno virtual y el código asignando los permisos al nuevo usuario
COPY --from=builder --chown=appuser:appgroup /app/.venv /app/.venv
COPY --chown=appuser:appgroup . /app

USER appuser

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]