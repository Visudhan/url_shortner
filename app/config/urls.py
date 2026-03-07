"""
Root URL configuration.

Routes:
  /admin/      → Django admin panel
  /api/urls/   → Shortener API (create shortened URLs)
  /<slug>      → Redirect to original URL
"""

from django.contrib import admin
from django.urls import path, include
from shortener.views import RedirectView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/urls/", include("shortener.urls")),
    
    # Add analytics routes under /api/urls/ too
    path("api/urls/", include("analytics.urls")),
    
    # Catch-all for short codes / custom aliases.
    # MUST be at the bottom so it doesn't intercept /admin/ or /api/
    path("<str:short_code>", RedirectView.as_view(), name="redirect"),
    path("<str:short_code>/", RedirectView.as_view(), name="redirect-slash"),
]
