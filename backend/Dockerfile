# ── Backend ───────────────────────
FROM python:3.12-slim AS base

WORKDIR /app

# System deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl gcc g++ libpq-dev && \
    rm -rf /var/lib/apt/lists/*

# Python deps
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Voice deps (optional — only installed if enabled)
ARG ENABLE_VOICE=false
RUN if [ "$ENABLE_VOICE" = "true" ]; then \
    pip install --no-cache-dir transformers torch soundfile librosa; \
    fi

# App code
COPY backend/ .
COPY blockchain/contracts/TransparencyRegistry.json /app/blockchain/contracts/ 2>/dev/null || true

# Health check
COPY --from=curlimages/curl:latest /usr/bin/curl /usr/bin/curl
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD curl -f http://localhost:8000/api/v1/health || exit 1

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
