from django.db import models
from django.contrib.postgres.fields import ArrayField
import uuid
from users.models import User

class StandardCategory(models.Model):
    """Categories for organizing standards (e.g., Working, Physical Fitness, etc.)"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='standard_categories')
    is_default = models.BooleanField(default=False)
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'standard_categories'
        unique_together = [['user', 'name']]
        ordering = ['order', 'name']

class Standard(models.Model):
    """Individual standards within categories"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    category = models.ForeignKey(StandardCategory, on_delete=models.CASCADE, related_name='standards')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='standards')
    title = models.CharField(max_length=200)
    description = models.TextField()
    minimum_requirement = models.TextField()
    success_criteria = ArrayField(models.CharField(max_length=500), default=list)
    
    FREQUENCY_CHOICES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('custom', 'Custom'),
    ]
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES)
    specific_days = ArrayField(
        models.IntegerField(choices=[(i, str(i)) for i in range(7)]),
        null=True,
        blank=True
    )
    time_of_day = models.TimeField(null=True, blank=True)
    duration_minutes = models.IntegerField(null=True, blank=True)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'standards'
        ordering = ['category', 'title']

class StandardProgress(models.Model):
    """Individual standard completion tracking"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    daily_progress = models.ForeignKey('goals.DailyProgress', on_delete=models.CASCADE, related_name='standard_progress')
    standard = models.ForeignKey(Standard, on_delete=models.CASCADE, related_name='progress')
    is_completed = models.BooleanField(default=False)
    completion_time = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    
    class Meta:
        db_table = 'standard_progress'
        unique_together = [['daily_progress', 'standard']]
