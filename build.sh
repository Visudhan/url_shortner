#!/usr/bin/env bash
# exit on error
set -o errexit

# Force production settings so Django connects to Supabase, not Docker's "db"
export DJANGO_SETTINGS_MODULE=config.settings.production

# Debug: check if env vars are available
echo "==> Checking environment variables..."
echo "DJANGO_SETTINGS_MODULE = $DJANGO_SETTINGS_MODULE"
if [ -z "$DATABASE_URL" ]; then
  echo "WARNING: DATABASE_URL is NOT set!"
else
  echo "DATABASE_URL is set (starts with: ${DATABASE_URL:0:20}...)"
fi

if [ -z "$REDIS_URL" ]; then
  echo "WARNING: REDIS_URL is NOT set!"
else
  echo "REDIS_URL is set (starts with: ${REDIS_URL:0:15}...)"
fi

# Install Python dependencies
pip install -r requirements.txt

# Collect Django static files (admin CSS, etc.)
cd app
python manage.py collectstatic --no-input

# Run database migrations against the cloud database
python manage.py migrate
