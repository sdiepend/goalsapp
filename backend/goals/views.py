from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Count, Avg, Q
from django.utils import timezone
from datetime import timedelta, datetime
from .models import Goal, DailyProgress, ProcessProgress, Reflection
from .serializers import (
    GoalSerializer,
    DailyProgressSerializer,
    ProcessProgressSerializer,
    ReflectionSerializer
)

class GoalListCreateView(generics.ListCreateAPIView):
    serializer_class = GoalSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return Goal.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class GoalDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = GoalSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return Goal.objects.filter(user=self.request.user)

    def perform_update(self, serializer):
        # Get the original instance before update
        instance = self.get_object()
        was_completed = instance.is_completed
        
        # Save the update
        updated_instance = serializer.save()
        
        # If goal was just completed, award points
        if not was_completed and updated_instance.is_completed:
            from gamification.services import GamificationService
            gamification = GamificationService(self.request.user)
            
            if updated_instance.goal_type == 'BIG':
                gamification.complete_big(updated_instance)
            elif updated_instance.goal_type == 'MTG':
                gamification.complete_mtg(updated_instance)
        
        return updated_instance

class GoalsByTypeView(generics.ListAPIView):
    serializer_class = GoalSerializer
    permission_classes = (permissions.IsAuthenticated,)
    pagination_class = None  # Disable pagination for goals by type

    def get_queryset(self):
        goal_type = self.kwargs['goal_type']
        return Goal.objects.filter(
            user=self.request.user,
            goal_type=goal_type
        )

class GoalChildrenView(generics.ListAPIView):
    serializer_class = GoalSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        parent_id = self.kwargs['pk']
        return Goal.objects.filter(
            user=self.request.user,
            parent_id=parent_id
        )

class DailyProgressListCreateView(generics.ListCreateAPIView):
    serializer_class = DailyProgressSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return DailyProgress.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class DailyProgressDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = DailyProgressSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return DailyProgress.objects.filter(user=self.request.user)

class DailyProgressByDateView(generics.RetrieveAPIView):
    serializer_class = DailyProgressSerializer
    permission_classes = (permissions.IsAuthenticated,)
    pagination_class = None  # Disable pagination for daily progress

    def get_object(self):
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
        daily_progress, created = DailyProgress.objects.get_or_create(
            user=self.request.user,
            date=date
        )

        # Get all active DPs for the user
        active_dps = Goal.objects.filter(
            user=self.request.user,
            goal_type='DP',
            start_date__lte=date,
            target_date__gte=date,
            is_completed=False
        )

        # Create process progress entries for any DPs that don't have them
        existing_progress = set(ProcessProgress.objects.filter(
            daily_progress=daily_progress
        ).values_list('process_id', flat=True))

        progress_to_create = []
        for dp in active_dps:
            if dp.id not in existing_progress:
                progress_to_create.append(ProcessProgress(
                    daily_progress=daily_progress,
                    process=dp
                ))

        if progress_to_create:
            ProcessProgress.objects.bulk_create(progress_to_create)

        return daily_progress

class ProcessProgressListCreateView(generics.ListCreateAPIView):
    serializer_class = ProcessProgressSerializer
    permission_classes = (permissions.IsAuthenticated,)
    pagination_class = None  # Disable pagination for process progress

    def get_queryset(self):
        return ProcessProgress.objects.filter(
            daily_progress__user=self.request.user
        )

    def perform_create(self, serializer):
        serializer.save()

class ProcessProgressDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ProcessProgressSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return ProcessProgress.objects.filter(
            daily_progress__user=self.request.user
        )

    def perform_update(self, serializer):
        # Get the original instance before update
        instance = self.get_object()
        was_completed = instance.is_completed
        
        # Update the instance
        if 'is_completed' in self.request.data:
            instance.is_completed = self.request.data['is_completed']
            if instance.is_completed:
                instance.completion_time = timezone.now()
        if 'time_spent_minutes' in self.request.data:
            instance.time_spent_minutes = self.request.data['time_spent_minutes']
        instance.save()
        
        # If process was just completed, award points
        if not was_completed and instance.is_completed:
            from gamification.services import GamificationService
            gamification = GamificationService(instance.daily_progress.user)
            gamification.complete_process(instance)

class ReflectionListCreateView(generics.ListCreateAPIView):
    serializer_class = ReflectionSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return Reflection.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class ReflectionDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ReflectionSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return Reflection.objects.filter(user=self.request.user)

class ReflectionsByTypeView(generics.ListAPIView):
    serializer_class = ReflectionSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        reflection_type = self.kwargs['reflection_type']
        return Reflection.objects.filter(
            user=self.request.user,
            reflection_type=reflection_type
        )

class GoalCompletionRateView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        goals = Goal.objects.filter(user=request.user)
        total_goals = goals.count()
        completed_goals = goals.filter(is_completed=True).count()
        
        completion_rate = 0
        if total_goals > 0:
            completion_rate = (completed_goals / total_goals) * 100
            
        return Response({
            'completion_rate': completion_rate,
            'total_goals': total_goals,
            'completed_goals': completed_goals
        })

class GoalChainHealthView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        # Check if BIG goals have associated MTGs and DPs
        big_goals = Goal.objects.filter(
            user=request.user,
            goal_type='BIG',
            is_completed=False
        )
        
        health_metrics = []
        for big in big_goals:
            mtgs = Goal.objects.filter(parent=big)
            total_dps = Goal.objects.filter(parent__in=mtgs, goal_type='DP')
            active_dps = total_dps.filter(is_completed=False)
            
            health_metrics.append({
                'big_goal': big.title,
                'mtg_count': mtgs.count(),
                'dp_count': total_dps.count(),
                'active_dp_count': active_dps.count(),
                'health_score': self._calculate_health_score(big, mtgs, active_dps)
            })
            
        return Response(health_metrics)
    
    def _calculate_health_score(self, big, mtgs, active_dps):
        # Simple health score calculation
        if mtgs.count() == 0:
            return 0
        
        mtg_score = min(mtgs.count() / 2, 1) * 0.4  # 40% weight for having proper MTGs
        dp_score = min(active_dps.count() / 2, 1) * 0.6  # 60% weight for active DPs
        
        return (mtg_score + dp_score) * 100

class TimeAllocationView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        # Get time allocation for the last 30 days
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=30)
        
        process_progress = ProcessProgress.objects.filter(
            daily_progress__user=request.user,
            daily_progress__date__range=(start_date, end_date)
        )
        
        time_by_category = process_progress.values(
            'process__category'
        ).annotate(
            total_minutes=Avg('time_spent_minutes')
        )
        
        return Response({
            'time_allocation': time_by_category,
            'date_range': {
                'start': start_date,
                'end': end_date
            }
        })

class ProgressHistoryView(APIView):
    """Get daily progress history for a date range"""
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        # Get date range from query params
        try:
            start_date = datetime.strptime(request.GET.get('start', ''), '%Y-%m-%d').date()
            end_date = datetime.strptime(request.GET.get('end', ''), '%Y-%m-%d').date()
        except ValueError:
            return Response(
                {'error': 'Invalid date format. Use YYYY-MM-DD.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Get all progress within date range
        daily_progress = DailyProgress.objects.filter(
            user=request.user,
            date__range=(start_date, end_date)
        ).prefetch_related('standard_progress', 'process_progress')

        # Build response data
        history = {}
        for progress in daily_progress:
            date_str = progress.date.isoformat()
            history[date_str] = {
                'standards_completed': progress.standard_progress.filter(is_completed=True).count(),
                'processes_completed': progress.process_progress.filter(is_completed=True).count(),
                'standards_total': progress.standard_progress.count(),
                'processes_total': progress.process_progress.count()
            }

        # Return empty data for dates without progress
        current = start_date
        while current <= end_date:
            date_str = current.isoformat()
            if date_str not in history:
                history[date_str] = {
                    'standards_completed': 0,
                    'processes_completed': 0,
                    'standards_total': 0,
                    'processes_total': 0
                }
            current += timedelta(days=1)

        return Response(history)
