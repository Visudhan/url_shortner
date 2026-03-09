#!/usr/bin/env bash
# exit on error
set -o errexit

# Force production settings so Django connects to Supabase, not Docker's "db"
export DJANGO_SETTINGS_MODULE=config.settings.production

# Install Python dependencies
pip install -r requirements.txt

# Collect Django static files (admin CSS, etc.)
cd app
python manage.py collectstatic --no-input

# Run database migrations against the cloud database
python manage.py migrate
