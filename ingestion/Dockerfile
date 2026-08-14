# ============================================
# BMKG ingestion runtime container
# ============================================
# Phase 1 image. Single-purpose: fetch BMKG data,
# parse, upload to MinIO. Replaced by Airflow
# worker in Phase 8.
# ============================================

FROM python:3.11-slim-bookworm AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    TZ=Asia/Jakarta

# System deps: curl for healthcheck, lxml needs libxml2/libxslt.
RUN apt-get update && apt-get install -y --no-install-recommends \
        curl \
        libxml2 \
        libxslt1.1 \
        tzdata \
    && ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install dependencies first for better layer caching.
COPY requirements/phase-1.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt \
    && rm /tmp/requirements.txt

# Copy source
COPY . /app

# Run as non-root for security
RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app
USER app

CMD ["python", "-m", "bmkg"]

