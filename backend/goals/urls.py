from django.urls import path
from . import views

app_name = 'goals'

urlpatterns = [
    # Goals
    path('', views.GoalListCreateView.as_view(), name='goal-list'),
    path('<uuid:pk>/', views.GoalDetailView.as_view(), name='goal-detail'),
    path('type/<str:goal_type>/', views.GoalsByTypeView.as_view(), name='goals-by-type'),
    path('<uuid:pk>/children/', views.GoalChildrenView.as_view(), name='goal-children'),
    
    # Daily Progress
    path('daily-progress/', views.DailyProgressListCreateView.as_view(), name='daily-progress-list'),
    path('daily-progress/<uuid:pk>/', views.DailyProgressDetailView.as_view(), name='daily-progress-detail'),
    path('daily-progress/date/<str:date>/', views.DailyProgressByDateView.as_view(), name='daily-progress-by-date'),
    
    # Process Progress
    path('process-progress/', views.ProcessProgressListCreateView.as_view(), name='process-progress-list'),
    path('process-progress/<uuid:pk>/', views.ProcessProgressDetailView.as_view(), name='process-progress-detail'),
    
    # Reflections
    path('reflections/', views.ReflectionListCreateView.as_view(), name='reflection-list'),
    path('reflections/<uuid:pk>/', views.ReflectionDetailView.as_view(), name='reflection-detail'),
    path('reflections/type/<str:reflection_type>/', views.ReflectionsByTypeView.as_view(), name='reflections-by-type'),
    
    # Analytics
    path('analytics/goal-completion/', views.GoalCompletionRateView.as_view(), name='goal-completion-rate'),
    path('analytics/goal-chain-health/', views.GoalChainHealthView.as_view(), name='goal-chain-health'),
    path('analytics/time-allocation/', views.TimeAllocationView.as_view(), name='time-allocation'),
    path('progress/history/', views.ProgressHistoryView.as_view(), name='progress-history'),
]
