from django.contrib import admin
from .models import UserProfile, Achievement, UserAchievement, PointTransaction

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'total_points', 'level', 'current_streak', 'longest_streak')
    list_filter = ('level',)
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('total_points', 'level', 'current_streak', 'longest_streak', 'last_activity_date')

@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
    list_display = ('name', 'achievement_type', 'points', 'required_count')
    list_filter = ('achievement_type',)
    search_fields = ('name', 'description')

@admin.register(UserAchievement)
class UserAchievementAdmin(admin.ModelAdmin):
    list_display = ('user', 'achievement', 'unlocked_at')
    list_filter = ('achievement__achievement_type', 'unlocked_at')
    search_fields = ('user__username', 'achievement__name')
    raw_id_fields = ('user', 'achievement')

@admin.register(PointTransaction)
class PointTransactionAdmin(admin.ModelAdmin):
    list_display = ('user', 'points', 'transaction_type', 'streak_multiplier', 'created_at')
    list_filter = ('transaction_type', 'created_at')
    search_fields = ('user__username', 'description')
    readonly_fields = ('points', 'streak_multiplier', 'created_at')
    raw_id_fields = ('user',)
