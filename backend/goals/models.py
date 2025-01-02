from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.contrib.postgres.fields import ArrayField
import uuid
from users.models import User

class Goal(models.Model):
    """Goals in the BIG-MTG-DP hierarchy"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='goals')
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='children')
    
    GOAL_TYPE_CHOICES = [
        ('BIG', 'Big Important Goal'),
        ('MTG', 'Medium Term Goal'),
        ('DP', 'Daily Process'),
    ]
    goal_type = models.CharField(max_length=3, choices=GOAL_TYPE_CHOICES)
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.CharField(max_length=100)  # e.g., Financial, Physical Fitness, etc.
    
    start_date = models.DateField()
    target_date = models.DateField()
    
    metrics = models.JSONField(default=list)  # Array of measurement criteria
    is_completed = models.BooleanField(default=False)
    completion_date = models.DateField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        if self.goal_type == 'BIG' and self.parent is not None:
            raise ValidationError(_('BIG goals cannot have a parent goal.'))
        if self.goal_type == 'MTG' and (self.parent is None or self.parent.goal_type != 'BIG'):
            raise ValidationError(_('MTG goals must have a BIG goal as parent.'))
        if self.goal_type == 'DP' and (self.parent is None or self.parent.goal_type != 'MTG'):
            raise ValidationError(_('DP goals must have a MTG goal as parent.'))

    class Meta:
        db_table = 'goals'

class DailyProgress(models.Model):
    """Daily tracking of standards and processes"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='daily_progress')
    date = models.DateField()
    
    class Meta:
        db_table = 'daily_progress'
        unique_together = [['user', 'date']]

class ProcessProgress(models.Model):
    """Individual daily process completion tracking"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    daily_progress = models.ForeignKey(DailyProgress, on_delete=models.CASCADE, related_name='process_progress')
    process = models.ForeignKey(Goal, on_delete=models.CASCADE, related_name='progress')
    is_completed = models.BooleanField(default=False)
    time_spent_minutes = models.IntegerField(default=0)
    completion_time = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)

    def clean(self):
        if self.process.goal_type != 'DP':
            raise ValidationError(_('Process progress can only be tracked for Daily Process goals.'))

    class Meta:
        db_table = 'process_progress'
        unique_together = [['daily_progress', 'process']]

class Reflection(models.Model):
    """Weekly/Monthly reflections on progress"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reflections')
    
    REFLECTION_TYPE_CHOICES = [
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('yearly', 'Yearly'),
    ]
    reflection_type = models.CharField(max_length=20, choices=REFLECTION_TYPE_CHOICES)
    
    start_date = models.DateField()
    end_date = models.DateField()
    content = models.TextField()
    highlights = ArrayField(models.TextField(), default=list)
    challenges = ArrayField(models.TextField(), default=list)
    action_items = ArrayField(models.TextField(), default=list)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'reflections'
        unique_together = [['user', 'reflection_type', 'start_date']]
