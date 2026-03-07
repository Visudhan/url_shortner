"""
URL routing for the Shortener app.

Maps URL paths to views:
  POST /api/urls/  →  URLCreateView (create a shortened URL)
"""

from django.urls import path
from shortener.views import URLCreateView


urlpatterns = [
    path("", URLCreateView.as_view(), name="url-create"),
]
