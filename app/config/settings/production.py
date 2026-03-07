"""
Production settings for URL Shortener.

Imports everything from base.py, then locks down security.
To use: set DJANGO_SETTINGS_MODULE=config.settings.production
"""

import os
from .base import *  # noqa: F401, F403 — import all base settings


# ─────────────────────────────────────────────
# DEBUG — OFF in production!
# ─────────────────────────────────────────────
# If DEBUG is True in production:
#   - Error pages show your source code to attackers
#   - Django stores every SQL query in memory (memory leak)
#   - Static files are served inefficiently
DEBUG = False


# ─────────────────────────────────────────────
# ALLOWED HOSTS
# ─────────────────────────────────────────────
# Only accept requests for YOUR domain(s).
# Without this, attackers can use your server for DNS rebinding attacks.
# Set via environment variable, comma-separated.
# Example: ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "").split(",")


# ─────────────────────────────────────────────
# SECURITY SETTINGS
# ─────────────────────────────────────────────
# Force HTTPS — redirect all HTTP requests to HTTPS
SECURE_SSL_REDIRECT = True

# HSTS — tell browsers to ONLY use HTTPS for this domain
# 31536000 seconds = 1 year
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Cookie security — prevent JavaScript access and ensure HTTPS-only
SESSION_COOKIE_SECURE = True       # Session cookie only sent over HTTPS
CSRF_COOKIE_SECURE = True          # CSRF cookie only sent over HTTPS
SESSION_COOKIE_HTTPONLY = True      # JavaScript can't read session cookie
CSRF_COOKIE_HTTPONLY = True         # JavaScript can't read CSRF cookie

# Prevent content-type sniffing attacks
SECURE_CONTENT_TYPE_NOSNIFF = True
