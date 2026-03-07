import uuid
from django.conf import settings
from django.db import models
from django.utils import timezone


class URL(models.Model):
    """
    Core model representing a shortened URL.

    Design decisions:
    - UUID primary key: never expose auto-increment integers in APIs
    - short_code: the actual slug (e.g. aB3xZ9), DB-indexed for fast lookups
    - custom_alias: user-defined override for short_code (e.g. /my-brand)
    - expires_at: nullable — URLs live forever unless expiry is set
    - is_active: soft-delete pattern — deactivate without losing analytics data
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    original_url = models.TextField(
        help_text="The full destination URL."
    )
    short_code = models.CharField(
        max_length=10,
        unique=True,
        db_index=True,
        help_text="Auto-generated unique slug used in the short URL."
    )
    custom_alias = models.CharField(
        max_length=50,
        unique=True,
        null=True,
        blank=True,
        db_index=True,
        help_text="Optional user-defined alias. Overrides short_code if set."
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="urls",
        help_text="Null for anonymous/public URL creation."
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="If set, redirects will fail after this datetime."
    )

    is_active = models.BooleanField(
        default=True,
        help_text="Deactivate to stop redirects without deleting the record."
    )

    class Meta:
        db_table = "urls"
        ordering = ["-created_at"]
        indexes = [
            # Composite index for active + expiry lookup (used on every redirect)
            models.Index(fields=["short_code", "is_active"], name="idx_short_code_active"),
            models.Index(fields=["custom_alias", "is_active"], name="idx_alias_active"),
        ]

    def __str__(self):
        return f"{self.short_code} -> {self.original_url[:60]}"

    @property
    def effective_short_code(self):
        """Returns custom_alias if set, otherwise short_code."""
        return self.custom_alias or self.short_code

    @property
    def is_expired(self):
        """Check if this URL has passed its expiry time."""
        if self.expires_at is None:
            return False
        return timezone.now() > self.expires_at

    @property
    def is_accessible(self):
        """A URL is accessible only if active AND not expired."""
        return self.is_active and not self.is_expired