#!/usr/bin/env bash
# exit on error
set -o errexit

# Force production settings
export DJANGO_SETTINGS_MODULE=config.settings.production

# Install Python dependencies
pip install -r requirements.txt

# Debug: test the EXACT database connection values
echo "==> DEBUG: Testing database connection..."
python3 -c "
import os

user = os.getenv('POSTGRES_USER', 'shortener_admin').strip()
password = os.getenv('POSTGRES_PASSWORD', 'shortener_pass_2024').strip()
host = os.getenv('POSTGRES_HOST', 'db').strip()
port = os.getenv('POSTGRES_PORT', '5432').strip()
dbname = os.getenv('POSTGRES_DB', 'url_shortener').strip()

print(f'  USER:     [{user}] (len={len(user)})')
print(f'  PASSWORD: [{password[:3]}***{password[-3:]}] (len={len(password)})')
print(f'  HOST:     [{host}] (len={len(host)})')
print(f'  PORT:     [{port}]')
print(f'  DBNAME:   [{dbname}]')

# Try to connect directly with psycopg2
import psycopg2
try:
    conn = psycopg2.connect(
        dbname=dbname,
        user=user,
        password=password,
        host=host,
        port=port,
        connect_timeout=10
    )
    print('  CONNECTION: SUCCESS!')
    conn.close()
except Exception as e:
    print(f'  CONNECTION FAILED: {e}')
    raise
"

# Collect Django static files
cd app
python manage.py collectstatic --no-input

# Run database migrations
python manage.py migrate
