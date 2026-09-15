# ---------------------------------------------
# Builder Stage
# ---------------------------------------------
FROM python:3.12-slim AS builder

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

RUN pip install --no-cache-dir poetry poetry-plugin-export

COPY auth_service/pyproject.toml auth_service/poetry.lock ./
COPY shared /shared

RUN --mount=type=cache,target=/root/.cache/pypoetry \
    poetry export -f requirements.txt --without-hashes -o requirements.txt

# ---------------------------------------------
# Final Stage
# ---------------------------------------------
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

WORKDIR /app

RUN groupadd -r appuser && useradd -r -g appuser appuser

COPY --from=builder /app/requirements.txt .

COPY --chown=appuser:appuser shared /shared

RUN pip install --no-cache-dir -r requirements.txt

COPY --chown=appuser:appuser auth_service/src ./src

USER appuser

EXPOSE 8000
