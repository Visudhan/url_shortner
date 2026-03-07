from django.db import models
from shortener.models import URL


class Click(models.Model):
    """
    Records every redirect event for a shortened URL.

    Design decisions:
    - BigAutoField: click volume can be enormous, avoid int overflow
    - No UUID here — clicks are internal records, never exposed directly
    - ip_address, user_agent, referer: raw data collected at click time
    - country: resolved asynchronously (via Celery task) — not at redirect time
      to keep redirect latency minimal
    - No FK to User — clicks are anonymous events tied to a URL, not a user session
    """

    id = models.BigAutoField(primary_key=True)

    url = models.ForeignKey(
        URL,
        on_delete=models.CASCADE,
        related_name="clicks",
        db_index=True,
    )

    clicked_at = models.DateTimeField(auto_now_add=True, db_index=True)

    # --- Request metadata ---
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        help_text="Raw IP of the visitor. Used for geo-resolution and abuse detection."
    )
    user_agent = models.TextField(
        null=True,
        blank=True,
        help_text="Full User-Agent string for device/browser analytics."
    )
    referer = models.URLField(
        max_length=2048,
        null=True,
        blank=True,
        help_text="HTTP Referer header — where the click originated from."
    )

    # --- Resolved fields (populated asynchronously) ---
    country = models.CharField(
        max_length=2,
        null=True,
        blank=True,
        help_text="ISO 3166-1 alpha-2 country code, resolved from IP asynchronously."
    )
    city = models.CharField(
        max_length=100,
        null=True,
        blank=True,
    )

    class Meta:
        db_table = "clicks"
        ordering = ["-clicked_at"]
        indexes = [
            # For analytics queries: "all clicks for URL X in date range Y-Z"
            models.Index(fields=["url", "clicked_at"], name="idx_url_clicked_at"),
            # For geo analytics
            models.Index(fields=["url", "country"], name="idx_url_country"),
        ]

    def __str__(self):
        return f"Click on {self.url.short_code} at {self.clicked_at}"
