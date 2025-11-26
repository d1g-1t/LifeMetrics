FROM python:3.11-slim AS base

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONFAULTHANDLER=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    UV_SYSTEM_PYTHON=1 \
    UV_COMPILE_BYTECODE=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && useradd -m -u 1000 appuser

COPY --from=ghcr.io/astral-sh/uv:0.4 /uv /usr/local/bin/uv

WORKDIR /app

COPY pyproject.toml ./

RUN uv pip install --system -e . 2>/dev/null || uv pip install --system \
    "django>=5.0,<5.1" \
    "django-ninja>=1.3.0" \
    "uvicorn[standard]>=0.27.0" \
    "gunicorn>=21.2.0" \
    "psycopg[binary,pool]>=3.1.18" \
    "redis[hiredis]>=5.0.1" \
    "django-redis>=5.4.0" \
    "celery[redis]>=5.3.6" \
    "django-celery-beat>=2.6.0" \
    "django-celery-results>=2.5.1" \
    "aiogram>=3.4.1" \
    "aiohttp>=3.9.1" \
    "pydantic>=2.5.3" \
    "pydantic-settings>=2.1.0" \
    "pyjwt>=2.8.0" \
    "argon2-cffi>=23.1.0" \
    "django-cors-headers>=4.3.1" \
    "sentry-sdk>=1.39.2" \
    "structlog>=24.1.0" \
    "python-json-logger>=2.0.7" \
    "python-dotenv>=1.0.0" \
    "django-environ>=0.11.2" \
    "orjson>=3.9.10" \
    "httptools>=0.6.1"

COPY --chown=appuser:appuser . .

RUN mkdir -p /app/staticfiles /app/media && chown -R appuser:appuser /app

USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/api/health || exit 1

CMD ["python", "-m", "uvicorn", "config.asgi:application", "--host", "0.0.0.0", "--port", "8000"]
