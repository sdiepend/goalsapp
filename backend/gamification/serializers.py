from rest_framework import serializers
from .models import UserProfile, Achievement, UserAchievement, PointTransaction

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = (
            'id', 'total_points', 'level', 'current_streak',
            'longest_streak', 'last_activity_date'
        )
        read_only_fields = fields

class AchievementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Achievement
        fields = (
            'id', 'name', 'description', 'points', 'icon',
            'achievement_type', 'required_count'
        )
        read_only_fields = fields

class UserAchievementSerializer(serializers.ModelSerializer):
    achievement = AchievementSerializer(read_only=True)
    
    class Meta:
        model = UserAchievement
        fields = ('id', 'achievement', 'unlocked_at')
        read_only_fields = fields

class PointTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PointTransaction
        fields = (
            'id', 'points', 'transaction_type', 'reference_id',
            'reference_type', 'streak_multiplier', 'description',
            'created_at'
        )
        read_only_fields = fields

class GamificationStatsSerializer(serializers.Serializer):
    """Combined stats for the dashboard"""
    profile = UserProfileSerializer()
    recent_achievements = UserAchievementSerializer(many=True)
    recent_transactions = PointTransactionSerializer(many=True)
    next_level_points = serializers.IntegerField()
    progress_to_next_level = serializers.FloatField()
