#!/usr/bin/env bash
# exit on error
set -o errexit

# Force production settings so Django connects to Supabase, not Docker's "db"
export DJANGO_SETTINGS_MODULE=config.settings.production

# Install Python dependencies
pip install -r requirements.txt

# Debug: show how Python parses the DATABASE_URL
echo "==> DEBUG: Parsing DATABASE_URL..."
python3 -c "
import os
from urllib.parse import urlparse, unquote
url = os.getenv('DATABASE_URL', '')
if url:
    p = urlparse(url)
    print(f'  scheme:   {p.scheme}')
    print(f'  username: {p.username}')
    print(f'  password: {\"***\" if p.password else \"NONE\"}')
    print(f'  hostname: {p.hostname}')
    print(f'  port:     {p.port}')
    print(f'  dbname:   {p.path}')
else:
    print('  DATABASE_URL is empty!')
"

# Collect Django static files (admin CSS, etc.)
cd app
python manage.py collectstatic --no-input

# Run database migrations against the cloud database
python manage.py migrate
