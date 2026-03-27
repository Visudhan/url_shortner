"""
Production settings for URL Shortener.

Imports everything from base.py, then locks down security.
To use: set DJANGO_SETTINGS_MODULE=config.settings.production
"""

import os
import dj_database_url
from .base import *  # noqa: F401, F403 — import all base settings


# ─────────────────────────────────────────────
# DEBUG — OFF in production!
# ─────────────────────────────────────────────
DEBUG = False


# ─────────────────────────────────────────────
# ALLOWED HOSTS
# ─────────────────────────────────────────────
# Set via environment variable, comma-separated.
# Example: ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
ALLOWED_HOSTS = [h.strip() for h in os.getenv("ALLOWED_HOSTS", "").split(",") if h.strip()]


# ─────────────────────────────────────────────
# DATABASE — Parse DATABASE_URL from Supabase
# ─────────────────────────────────────────────
# dj-database-url converts the single DATABASE_URL string
# into the dict Django expects (ENGINE, NAME, USER, etc.)
DATABASE_URL = os.getenv("DATABASE_URL", "").strip().strip('"').strip("'")
if DATABASE_URL and DATABASE_URL.startswith("postgres"):
    DATABASES = {
        "default": dj_database_url.parse(DATABASE_URL)
    }


# ─────────────────────────────────────────────
# REDIS — Parse REDIS_URL from Upstash (SSL)
# ─────────────────────────────────────────────
REDIS_URL = os.getenv("REDIS_URL")
if REDIS_URL:
    CACHES = {
        "default": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": REDIS_URL,
            "OPTIONS": {
                "CLIENT_CLASS": "django_redis.client.DefaultClient",
            },
        }
    }
    CELERY_BROKER_URL = REDIS_URL
    CELERY_RESULT_BACKEND = REDIS_URL


# ─────────────────────────────────────────────
# CORS — Allow the frontend domain to call our API
# ─────────────────────────────────────────────
CORS_ALLOWED_ORIGINS = os.getenv("CORS_ALLOWED_ORIGINS", "").split(",")


# ─────────────────────────────────────────────
# STATIC FILES — Use WhiteNoise to serve static files
# ─────────────────────────────────────────────
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"


# ─────────────────────────────────────────────
# SECURITY SETTINGS
# ─────────────────────────────────────────────
# Render handles HTTPS at the load balancer level,
# so we trust the X-Forwarded-Proto header instead of
# forcing SSL redirect (which would cause infinite loops)
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = False  # Render handles this

# HSTS — tell browsers to ONLY use HTTPS for this domain
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Cookie security
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True
SECURE_CONTENT_TYPE_NOSNIFF = True
