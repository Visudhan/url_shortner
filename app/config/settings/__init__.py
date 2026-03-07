"""
Default settings module.

When manage.py or wsgi.py uses DJANGO_SETTINGS_MODULE = 'config.settings',
Python imports this __init__.py, which pulls in development settings.

To switch to production:
  Set DJANGO_SETTINGS_MODULE=config.settings.production
"""

from .development import *  # noqa: F401, F403
