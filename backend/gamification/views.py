from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils import timezone
from datetime import timedelta
import math

from .models import UserProfile, Achievement, UserAchievement, PointTransaction
from .serializers import (
    UserProfileSerializer,
    AchievementSerializer,
    UserAchievementSerializer,
    PointTransactionSerializer,
    GamificationStatsSerializer
)

class GamificationStatsView(APIView):
    """Combined gamification stats for the dashboard"""
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        profile = UserProfile.objects.get(user=request.user)
        
        # Calculate points needed for next level
        current_level = profile.level
        points_for_next_level = ((current_level) ** 2) * 100
        progress = (profile.total_points - ((current_level - 1) ** 2) * 100) / (points_for_next_level - ((current_level - 1) ** 2) * 100) * 100
        
        # Get recent achievements and transactions
        recent_achievements = UserAchievement.objects.filter(
            user=request.user
        ).order_by('-unlocked_at')[:5]
        
        recent_transactions = PointTransaction.objects.filter(
            user=request.user
        ).order_by('-created_at')[:10]
        
        data = {
            'profile': profile,
            'recent_achievements': recent_achievements,
            'recent_transactions': recent_transactions,
            'next_level_points': points_for_next_level,
            'progress_to_next_level': progress
        }
        
        serializer = GamificationStatsSerializer(data)
        return Response(serializer.data)

class UserAchievementsView(generics.ListAPIView):
    """List all achievements for the current user"""
    serializer_class = UserAchievementSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return UserAchievement.objects.filter(
            user=self.request.user
        ).order_by('-unlocked_at')

class AvailableAchievementsView(generics.ListAPIView):
    """List all achievements that haven't been unlocked yet"""
    serializer_class = AchievementSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        earned_ids = UserAchievement.objects.filter(
            user=self.request.user
        ).values_list('achievement_id', flat=True)
        
        return Achievement.objects.exclude(
            id__in=earned_ids
        )

class PointTransactionHistoryView(generics.ListAPIView):
    """List point transactions with optional filtering"""
    serializer_class = PointTransactionSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        queryset = PointTransaction.objects.filter(
            user=self.request.user
        )
        
        # Filter by transaction type
        transaction_type = self.request.query_params.get('type', None)
        if transaction_type:
            queryset = queryset.filter(transaction_type=transaction_type)
        
        # Filter by date range
        days = self.request.query_params.get('days', None)
        if days:
            try:
                days = int(days)
                start_date = timezone.now() - timedelta(days=days)
                queryset = queryset.filter(created_at__gte=start_date)
            except ValueError:
                pass
        
        return queryset.order_by('-created_at')

class LeaderboardView(APIView):
    """Global leaderboard based on total points"""
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        # Get top 10 users by points
        top_users = UserProfile.objects.order_by('-total_points')[:10]
        
        # Get requesting user's rank
        user_profile = UserProfile.objects.get(user=request.user)
        user_rank = UserProfile.objects.filter(
            total_points__gt=user_profile.total_points
        ).count() + 1
        
        return Response({
            'leaderboard': UserProfileSerializer(top_users, many=True).data,
            'user_rank': user_rank,
            'user_profile': UserProfileSerializer(user_profile).data
        })
