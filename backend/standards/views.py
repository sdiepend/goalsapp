from rest_framework import generics, permissions, status, serializers
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Count, Avg, Q
from django.utils import timezone
from datetime import timedelta
from .models import StandardCategory, Standard, StandardProgress
from .serializers import (
    StandardCategorySerializer,
    StandardSerializer,
    StandardProgressSerializer
)

class StandardCategoryListCreateView(generics.ListCreateAPIView):
    serializer_class = StandardCategorySerializer
    permission_classes = (permissions.IsAuthenticated,)
    pagination_class = None  # Disable pagination for categories

    def get_queryset(self):
        return StandardCategory.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class StandardCategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = StandardCategorySerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return StandardCategory.objects.filter(user=self.request.user)

class StandardListCreateView(generics.ListCreateAPIView):
    serializer_class = StandardSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return Standard.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class StandardDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = StandardSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return Standard.objects.filter(user=self.request.user)

class StandardsByCategoryView(generics.ListAPIView):
    serializer_class = StandardSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        category_id = self.kwargs['category_id']
        return Standard.objects.filter(
            user=self.request.user,
            category_id=category_id
        )

class StandardProgressListCreateView(generics.ListCreateAPIView):
    serializer_class = StandardProgressSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return StandardProgress.objects.filter(
            standard__user=self.request.user
        )

    def perform_create(self, serializer):
        serializer.save()

class StandardProgressDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = StandardProgressSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return StandardProgress.objects.filter(
            standard__user=self.request.user
        )

    def perform_update(self, serializer):
        # Get the original instance before update
        instance = self.get_object()
        was_completed = instance.is_completed
        
        # Save the update
        updated_instance = serializer.save()
        
        # If standard was just completed, award points
        if not was_completed and updated_instance.is_completed:
            from gamification.services import GamificationService
            gamification = GamificationService(self.request.user)
            gamification.complete_standard(updated_instance.standard)
        
        return updated_instance

class StandardProgressByDateView(generics.ListAPIView):
    serializer_class = StandardProgressSerializer
    permission_classes = (permissions.IsAuthenticated,)
    pagination_class = None  # Disable pagination for progress

    def get_queryset(self):
        date = self.kwargs['date']
        today = timezone.now().date()
        
        try:
            requested_date = timezone.datetime.strptime(date, '%Y-%m-%d').date()
        except ValueError:
            raise serializers.ValidationError({'date': 'Invalid date format. Use YYYY-MM-DD.'})
        
        if requested_date > today:
            raise serializers.ValidationError({
                'date': 'Cannot access progress for future dates.'
            })

        # Get or create daily progress
        from goals.models import DailyProgress
        daily_progress, _ = DailyProgress.objects.get_or_create(
            user=self.request.user,
            date=requested_date
        )

        # Get all active standards
        active_standards = Standard.objects.filter(
            user=self.request.user,
            is_active=True
        )

        # Get existing progress entries
        existing_progress = set(StandardProgress.objects.filter(
            daily_progress=daily_progress
        ).values_list('standard_id', flat=True))

        # Create progress entries for standards that need them
        progress_to_create = []
        for standard in active_standards:
            if standard.id not in existing_progress:
                # For daily standards, always create progress
                if standard.frequency == 'daily':
                    progress_to_create.append(StandardProgress(
                        daily_progress=daily_progress,
                        standard=standard
                    ))
                # For weekly standards, only create progress if it's not completed this week
                elif standard.frequency == 'weekly':
                    # Get the start of the week (Monday)
                    week_start = requested_date - timedelta(days=requested_date.weekday())
                    week_end = week_start + timedelta(days=6)
                    
                    # Check if standard is already completed this week
                    week_progress = StandardProgress.objects.filter(
                        standard=standard,
                        daily_progress__date__range=(week_start, week_end),
                        is_completed=True
                    ).exists()
                    
                    if not week_progress:
                        progress_to_create.append(StandardProgress(
                            daily_progress=daily_progress,
                            standard=standard
                        ))

        if progress_to_create:
            StandardProgress.objects.bulk_create(progress_to_create)

        return StandardProgress.objects.filter(
            daily_progress=daily_progress
        ).select_related('standard', 'standard__category')

class StandardCompletionRateView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        # Calculate completion rates for the last 30 days
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=30)
        
        progress = StandardProgress.objects.filter(
            standard__user=request.user,
            daily_progress__date__range=(start_date, end_date)
        ).aggregate(
            total=Count('id'),
            completed=Count('id', filter=Q(is_completed=True))
        )
        
        completion_rate = 0
        if progress['total'] > 0:
            completion_rate = (progress['completed'] / progress['total']) * 100
            
        return Response({
            'completion_rate': completion_rate,
            'total_standards': progress['total'],
            'completed_standards': progress['completed']
        })

class StandardStreakView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        # Calculate current streak of completed standards
        today = timezone.now().date()
        streak = 0
        current_date = today
        
        while True:
            daily_completion = StandardProgress.objects.filter(
                standard__user=request.user,
                daily_progress__date=current_date
            ).aggregate(
                total=Count('id'),
                completed=Count('id', filter=Q(is_completed=True))
            )
            
            if daily_completion['total'] == 0 or daily_completion['completed'] < daily_completion['total']:
                break
                
            streak += 1
            current_date -= timedelta(days=1)
            
        return Response({
            'current_streak': streak,
            'last_completion_date': current_date + timedelta(days=1)
        })
