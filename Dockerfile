# ─────────────────────────────────────────────
# Stage: Python base image
# ─────────────────────────────────────────────
# python:3.11-slim is a lightweight Debian image (~150MB vs ~900MB for full)
# "slim" = no build tools, compilers, or dev headers pre-installed
FROM python:3.11-slim

# ─────────────────────────────────────────────
# System dependencies
# ─────────────────────────────────────────────
# psycopg2-binary needs libpq (PostgreSQL C client library)
# gcc is needed in case any Python package requires compilation
# --no-install-recommends = skip optional packages to keep image small
# rm -rf /var/lib/apt/lists/* = delete apt cache to shrink the layer
RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# ─────────────────────────────────────────────
# Working directory inside the container
# ─────────────────────────────────────────────
# All subsequent commands run from /app
# This maps to your local 'app/' folder
WORKDIR /app

# ─────────────────────────────────────────────
# Install Python dependencies
# ─────────────────────────────────────────────
# COPY requirements.txt first (before copying code) for Docker layer caching:
#   - If requirements.txt hasn't changed, Docker reuses the cached pip install
#   - This means code changes don't trigger a full pip install (saves minutes)
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# ─────────────────────────────────────────────
# Copy application code
# ─────────────────────────────────────────────
# Copy everything from local 'app/' into container's /app
# Note: In dev, docker-compose overrides this with a volume mount
# so you get live code reload without rebuilding the image
COPY app/ /app/

# ─────────────────────────────────────────────
# Expose port
# ─────────────────────────────────────────────
# Documents that the container listens on port 8000
# (doesn't actually publish the port — docker-compose does that)
EXPOSE 8000

# ─────────────────────────────────────────────
# Start command
# ─────────────────────────────────────────────
# In development: Django's built-in dev server with auto-reload
# 0.0.0.0 = listen on all interfaces (required inside Docker)
# Without 0.0.0.0, the server only listens on 127.0.0.1 inside
# the container, and your host machine can't reach it
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
