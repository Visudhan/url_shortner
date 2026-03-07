import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Extended user model.
    Using UUID as primary key to avoid exposing sequential IDs.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    api_key = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "users"

    def __str__(self):
        return self.username

    def regenerate_api_key(self):
        """Allow user to rotate their API key."""
        self.api_key = uuid.uuid4()
        self.save(update_fields=["api_key"])
