#!/usr/bin/env bash
# exit on error
set -o errexit

# Install Python dependencies
pip install -r requirements.txt

# Collect Django static files (admin CSS, etc.)
cd app
python manage.py collectstatic --no-input

# Run database migrations against the cloud database
python manage.py migrate
