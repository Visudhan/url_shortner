"""
URL routing for the Analytics app.

Maps URL paths to views:
  GET /api/urls/<short_code>/stats/  →  AnalyticsStatView (get click stats)
"""

from django.urls import path
from analytics.views import AnalyticsStatView


urlpatterns = [
    path("<str:short_code>/stats/", AnalyticsStatView.as_view(), name="url-stats"),
]
