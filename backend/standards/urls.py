from django.urls import path
from . import views

app_name = 'standards'

urlpatterns = [
    # Standard Categories
    path('categories/', views.StandardCategoryListCreateView.as_view(), name='category-list'),
    path('categories/<uuid:pk>/', views.StandardCategoryDetailView.as_view(), name='category-detail'),
    
    # Standards
    path('', views.StandardListCreateView.as_view(), name='standard-list'),
    path('<uuid:pk>/', views.StandardDetailView.as_view(), name='standard-detail'),
    path('by-category/<uuid:category_id>/', views.StandardsByCategoryView.as_view(), name='standards-by-category'),
    
    # Progress
    path('progress/', views.StandardProgressListCreateView.as_view(), name='progress-list'),
    path('progress/<uuid:pk>/', views.StandardProgressDetailView.as_view(), name='progress-detail'),
    path('progress/date/<str:date>/', views.StandardProgressByDateView.as_view(), name='progress-by-date'),
    
    # Analytics
    path('analytics/completion-rate/', views.StandardCompletionRateView.as_view(), name='completion-rate'),
    path('analytics/streak/', views.StandardStreakView.as_view(), name='streak'),
]
