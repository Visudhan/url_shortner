"""
Celery configuration.

This file tells Celery how to connect to our Django project
and where to find the tasks we write.
"""

import os
from celery import Celery

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

# Create the Celery app
app = Celery("url_shortener")

# Read config from Django settings, using a 'CELERY_' prefix
# E.g. CELERY_BROKER_URL in Django settings becomes broker_url in Celery
app.config_from_object("django.conf:settings", namespace="CELERY")

# Auto-discover tasks in all installed apps (looks for tasks.py files)
app.autodiscover_tasks()
