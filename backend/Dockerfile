# ── Stage 1: Builder ───────────────────────────────────────────────────────────
FROM python:3.13-slim AS builder

WORKDIR /app

# System deps for psycopg2-binary and pillow
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies into a prefix we'll copy later
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt


# ── Stage 2: Runtime ───────────────────────────────────────────────────────────
FROM python:3.13-slim

WORKDIR /app

# Runtime libs only (no build tools)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Copy installed packages from builder
COPY --from=builder /install /usr/local

# Copy application source
COPY . .

# Collect static files (WhiteNoise serves them; SECRET_KEY required by settings)
ARG SECRET_KEY=build-time-dummy-not-used-in-production
RUN SECRET_KEY=$SECRET_KEY \
    DEBUG=False \
    python manage.py collectstatic --no-input

# Create non-root user for security
RUN useradd --no-create-home --shell /bin/false appuser \
    && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

# startup.sh runs migrations then launches gunicorn
ENTRYPOINT ["./start.sh"]
