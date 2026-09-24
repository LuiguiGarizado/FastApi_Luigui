# ==========================================
# 1. Builder stage (Construcción con uv)
# ==========================================
FROM ghcr.io/astral-sh/uv:python3.12-slim AS builder

# Acelerar compilación de bytecode y deshabilitar enlaces duros en Docker
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

WORKDIR /app

# Instalar dependencias aprovechando la caché de Docker
COPY pyproject.toml uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project --no-dev

# Copiar el código del proyecto e instalarlo
COPY . /app
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev


# ==========================================
# 2. Stage Final (Imagen liviana para producción)
# ==========================================
FROM python:3.12-slim

WORKDIR /app

# Copiar únicamente el entorno virtual (.venv) e instalaciones del builder
COPY --from=builder /app/.venv /app/.venv

# Copiar el código fuente
COPY . /app

# Activar el entorno virtual en el PATH
ENV PATH="/app/.venv/bin:$PATH"

EXPOSE 8000

# Iniciar la aplicación con Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]