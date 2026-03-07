"""
Development settings for URL Shortener.

Imports everything from base.py, then overrides what's needed for local dev.
This file is loaded by default via settings/__init__.py.
"""

from .base import *  # noqa: F401, F403 — import all base settings


# ─────────────────────────────────────────────
# DEBUG MODE
# ─────────────────────────────────────────────
# Enables:
#   - Detailed error pages with full traceback in the browser
#   - Django Debug Toolbar support (if installed)
#   - Static files served by Django (no need for nginx)
#   - Auto-reload when code changes (runserver only)
DEBUG = True


# ─────────────────────────────────────────────
# ALLOWED HOSTS
# ─────────────────────────────────────────────
# In dev, accept requests from ANY hostname.
# This is fine locally but NEVER do this in production.
# '*' means: localhost, 127.0.0.1, your IP, any domain — all accepted.
ALLOWED_HOSTS = ["*"]
