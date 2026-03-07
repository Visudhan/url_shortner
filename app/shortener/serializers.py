"""
Serializers for the Shortener app.

What is a Serializer?
  Think of it as a translator between two worlds:

  1. INCOMING (JSON from API request) → Python/Django objects
     Client sends: {"original_url": "https://google.com", "custom_alias": "goog"}
     Serializer validates it and prepares it for saving to the database.

  2. OUTGOING (Django model) → JSON for API response
     Database has a URL object with 10+ fields.
     Serializer picks which fields to include in the response.

  It also handles VALIDATION:
     - Is original_url actually a valid URL?
     - Is custom_alias already taken?
     - Is custom_alias a valid format?
"""

from rest_framework import serializers
from shortener.models import URL


class URLSerializer(serializers.ModelSerializer):
    """
    Handles both creating a shortened URL and formatting the API response.

    Input (what the client sends):
      {
        "original_url": "https://example.com/very/long/path",   ← required
        "custom_alias": "my-brand",                              ← optional
        "expires_at": "2025-12-31T23:59:59Z"                    ← optional
      }

    Output (what the API returns):
      {
        "id": "a1b2c3d4-...",
        "original_url": "https://example.com/very/long/path",
        "short_code": "aB3xZ9",
        "custom_alias": "my-brand",
        "short_url": "http://localhost:8000/my-brand",
        "created_at": "2025-01-15T10:30:00Z",
        "expires_at": "2025-12-31T23:59:59Z",
        "is_active": true
      }
    """

    # This field doesn't exist on the model — we compute it in get_short_url()
    # read_only=True means: include in response, but don't expect it in input
    short_url = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = URL
        # Fields included in the API response
        fields = [
            "id",
            "original_url",
            "short_code",
            "custom_alias",
            "short_url",       # computed field
            "created_at",
            "expires_at",
            "is_active",
        ]
        # Fields the client cannot set — server generates them
        read_only_fields = [
            "id",              # auto-generated UUID
            "short_code",      # auto-generated Base62
            "is_active",       # defaults to True
            "created_at",      # auto_now_add
        ]

    def get_short_url(self, obj):
        """
        Build the full short URL for the response.

        Because we are running in Docker behind a proxy, request.build_absolute_uri()
        might generate 'http://web:8000/...' which your browser can't resolve.
        We explicitly use the public-facing domain (localhost:8000 for local dev).
        """
        code = obj.effective_short_code
        
        # In production this would come from settings.DOMAIN or .env
        # For development, we hardcode the known public port setup
        base_url = "http://localhost:8000"
        
        return f"{base_url}/{code}"

    def validate_custom_alias(self, value):
        """
        Validate the custom alias if provided.

        Rules:
          - Must be 3-50 characters
          - Only letters, numbers, and hyphens allowed
          - Must not already exist in the database
        """
        if value is None:
            return value

        # Length check
        if len(value) < 3:
            raise serializers.ValidationError(
                "Custom alias must be at least 3 characters long."
            )

        # Character check — only alphanumeric and hyphens
        if not all(c.isalnum() or c == "-" for c in value):
            raise serializers.ValidationError(
                "Custom alias can only contain letters, numbers, and hyphens."
            )

        # Uniqueness check
        if URL.objects.filter(custom_alias=value).exists():
            raise serializers.ValidationError(
                "This custom alias is already taken."
            )

        return value
