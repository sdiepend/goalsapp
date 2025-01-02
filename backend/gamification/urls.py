from django.urls import path
from . import views

app_name = 'gamification'

urlpatterns = [
    path('stats/', views.GamificationStatsView.as_view(), name='stats'),
    path('achievements/', views.UserAchievementsView.as_view(), name='achievements'),
    path('achievements/available/', views.AvailableAchievementsView.as_view(), name='available-achievements'),
    path('points/history/', views.PointTransactionHistoryView.as_view(), name='point-history'),
    path('leaderboard/', views.LeaderboardView.as_view(), name='leaderboard'),
]
