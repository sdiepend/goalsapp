from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid

class User(AbstractUser):
    """Extended user model with additional profile fields"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    timezone = models.CharField(max_length=50, default='UTC')
    preferred_reminder_time = models.TimeField(null=True, blank=True)
    notification_preferences = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'users'
