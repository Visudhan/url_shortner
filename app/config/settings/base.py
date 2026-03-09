"""
Base settings for URL Shortener project.

This file contains settings shared across ALL environments (dev, prod).
Environment-specific overrides go in development.py or production.py.

Settings that depend on secrets (DB password, SECRET_KEY) are loaded
from environment variables via python-dotenv — never hardcoded here.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# ─────────────────────────────────────────────
# PATH SETUP
# ─────────────────────────────────────────────
# BASE_DIR points to the 'app/' folder (where manage.py lives)
# Path(__file__) = .../app/config/settings/base.py
# .resolve().parent = .../app/config/settings/
# .parent         = .../app/config/
# .parent         = .../app/              ← this is BASE_DIR
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Load .env file from the PROJECT ROOT (one level above app/)
# This is where docker-compose also reads .env from
load_dotenv(BASE_DIR.parent / ".env")


# ─────────────────────────────────────────────
# SECURITY
# ─────────────────────────────────────────────
SECRET_KEY = os.getenv("SECRET_KEY", "fallback-insecure-key-for-dev-only")


# ─────────────────────────────────────────────
# INSTALLED APPS
# ─────────────────────────────────────────────
INSTALLED_APPS = [
    # Django built-in apps
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # Third-party apps
    "rest_framework",       # Django REST Framework — builds our API
    "corsheaders",          # CORS support for frontend

    # Our apps
    "users",                # Custom user model with UUID + API key
    "shortener",            # URL shortening logic
    "analytics",            # Click tracking and stats
]


# ─────────────────────────────────────────────
# CUSTOM USER MODEL
# ─────────────────────────────────────────────
# Tell Django to use our User model instead of the default one.
# Format: "app_label.ModelName"
# MUST be set BEFORE running the first migration — can't change later.
AUTH_USER_MODEL = "users.User"


# ─────────────────────────────────────────────
# MIDDLEWARE
# ─────────────────────────────────────────────
# Middleware runs on every request/response — order matters!
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",        # HTTPS redirects, HSTS
    "whitenoise.middleware.WhiteNoiseMiddleware",            # Serve static files in production
    "corsheaders.middleware.CorsMiddleware",                # CORS for React frontend
    "django.contrib.sessions.middleware.SessionMiddleware",  # Session handling
    "django.middleware.common.CommonMiddleware",             # URL normalization
    "django.middleware.csrf.CsrfViewMiddleware",            # CSRF protection
    "django.contrib.auth.middleware.AuthenticationMiddleware",  # Attach user to request
    "django.contrib.messages.middleware.MessageMiddleware",  # Flash messages
    "django.middleware.clickjacking.XFrameOptionsMiddleware",  # Clickjacking protection
]


# ─────────────────────────────────────────────
# URL CONFIGURATION
# ─────────────────────────────────────────────
ROOT_URLCONF = "config.urls"


# ─────────────────────────────────────────────
# TEMPLATES (needed for admin panel)
# ─────────────────────────────────────────────
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]


# ─────────────────────────────────────────────
# WSGI
# ─────────────────────────────────────────────
WSGI_APPLICATION = "config.wsgi.application"


# ─────────────────────────────────────────────
# DATABASE — PostgreSQL
# ─────────────────────────────────────────────
# All values come from .env via os.getenv()
# Inside Docker: POSTGRES_HOST = "db" (the service name)
# Outside Docker: you'd set POSTGRES_HOST = "localhost"
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("POSTGRES_DB", "url_shortener"),
        "USER": os.getenv("POSTGRES_USER", "shortener_admin"),
        "PASSWORD": os.getenv("POSTGRES_PASSWORD", "shortener_pass_2024"),
        "HOST": os.getenv("POSTGRES_HOST", "db"),
        "PORT": os.getenv("POSTGRES_PORT", "5432"),
    }
}


# ─────────────────────────────────────────────
# CACHE — Redis
# ─────────────────────────────────────────────
# This is the core of your redirect performance.
# Every redirect checks Redis FIRST before hitting PostgreSQL.
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": os.getenv("REDIS_URL", "redis://redis:6379/0"),
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
    }
}


# ─────────────────────────────────────────────
# CELERY
# ─────────────────────────────────────────────
# We use Redis as the message broker (queue) for background tasks
CELERY_BROKER_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")
CELERY_RESULT_BACKEND = os.getenv("REDIS_URL", "redis://redis:6379/0")
# Accept only JSON serialized tasks
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"


# ─────────────────────────────────────────────
# PASSWORD VALIDATION
# ─────────────────────────────────────────────
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]


# ─────────────────────────────────────────────
# INTERNATIONALIZATION
# ─────────────────────────────────────────────
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True


# ─────────────────────────────────────────────
# STATIC FILES
# ─────────────────────────────────────────────
STATIC_URL = "static/"
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")


# ─────────────────────────────────────────────
# DEFAULT PRIMARY KEY TYPE
# ─────────────────────────────────────────────
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
