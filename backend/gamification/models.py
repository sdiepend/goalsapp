from django.db import models
from django.db.models import Sum
from django.utils import timezone
from users.models import User
import uuid

class UserProfile(models.Model):
    """Extended user profile for gamification"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='game_profile')
    total_points = models.IntegerField(default=0)
    level = models.IntegerField(default=1)
    current_streak = models.IntegerField(default=0)
    longest_streak = models.IntegerField(default=0)
    last_activity_date = models.DateField(null=True, blank=True)

    def calculate_level(self):
        """Calculate level based on total points"""
        # Level formula: level = 1 + floor(sqrt(total_points / 100))
        # This means:
        # Level 1: 0-99 points
        # Level 2: 100-399 points
        # Level 3: 400-899 points
        # etc.
        import math
        self.level = 1 + math.floor(math.sqrt(self.total_points / 100))
        self.save()

    def update_streak(self, activity_date):
        """Update streak based on activity date"""
        today = timezone.now().date()
        
        # Can't update streak for future dates
        if activity_date > today:
            return
        
        # First activity
        if not self.last_activity_date:
            self.current_streak = 1
            self.longest_streak = 1
            self.last_activity_date = activity_date
            self.save()
            return
        
        # Calculate days between last activity and this one
        days_diff = (activity_date - self.last_activity_date).days
        
        # If activity is on the next day, increment streak
        if days_diff == 1:
            self.current_streak += 1
            if self.current_streak > self.longest_streak:
                self.longest_streak = self.current_streak
        # If activity is on the same day, no change
        elif days_diff == 0:
            pass
        # If there's a gap, reset streak
        else:
            self.current_streak = 1
        
        self.last_activity_date = activity_date
        self.save()

    class Meta:
        db_table = 'user_game_profiles'

class Achievement(models.Model):
    """Unlockable achievements"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    description = models.TextField()
    points = models.IntegerField(default=0)
    icon = models.CharField(max_length=50)  # Icon identifier
    
    # Achievement types
    ACHIEVEMENT_TYPES = [
        ('streak', 'Streak Achievement'),
        ('completion', 'Completion Achievement'),
        ('level', 'Level Achievement'),
        ('special', 'Special Achievement'),
    ]
    achievement_type = models.CharField(max_length=20, choices=ACHIEVEMENT_TYPES)
    
    # Requirements
    required_count = models.IntegerField(default=0)  # e.g., streak length, completion count
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'achievements'

class UserAchievement(models.Model):
    """Tracks which achievements users have unlocked"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='achievements')
    achievement = models.ForeignKey(Achievement, on_delete=models.CASCADE)
    unlocked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'user_achievements'
        unique_together = [['user', 'achievement']]

class PointTransaction(models.Model):
    """Records point transactions"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='point_transactions')
    points = models.IntegerField()
    
    # Transaction types
    TRANSACTION_TYPES = [
        ('standard', 'Standard Completion'),
        ('process', 'Daily Process'),
        ('mtg', 'Medium Term Goal'),
        ('big', 'Big Goal'),
        ('streak', 'Streak Bonus'),
        ('achievement', 'Achievement'),
    ]
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    
    # Optional reference to the completed item
    reference_id = models.UUIDField(null=True, blank=True)
    reference_type = models.CharField(max_length=50, null=True, blank=True)
    
    streak_multiplier = models.FloatField(default=1.0)
    description = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'point_transactions'

    def save(self, *args, **kwargs):
        # Apply streak multiplier
        self.points = int(self.points * self.streak_multiplier)
        
        # Save the transaction
        super().save(*args, **kwargs)
        
        # Update user's total points
        profile = self.user.game_profile
        profile.total_points = PointTransaction.objects.filter(
            user=self.user
        ).aggregate(total=Sum('points'))['total'] or 0
        profile.calculate_level()
