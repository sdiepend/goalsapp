from rest_framework import serializers
from django.utils import timezone
from .models import Goal, DailyProgress, ProcessProgress, Reflection

class GoalSerializer(serializers.ModelSerializer):
    children_count = serializers.SerializerMethodField()
    completion_percentage = serializers.SerializerMethodField()

    class Meta:
        model = Goal
        fields = (
            'id', 'parent', 'goal_type', 'title', 'description', 'category',
            'start_date', 'target_date', 'metrics', 'is_completed',
            'completion_date', 'created_at', 'updated_at', 'children_count',
            'completion_percentage'
        )
        read_only_fields = ('id', 'created_at', 'updated_at', 'children_count',
                          'completion_percentage')

    def get_children_count(self, obj):
        return obj.children.count()

    def get_completion_percentage(self, obj):
        if obj.goal_type == 'DP':
            # For DPs, calculate based on process progress
            total_days = (obj.target_date - obj.start_date).days + 1
            completed_days = obj.progress.filter(is_completed=True).count()
            return (completed_days / total_days * 100) if total_days > 0 else 0
        elif obj.goal_type == 'MTG':
            # For MTGs, calculate based on DP completion
            dps = obj.children.all()
            if not dps.exists():
                return 0
            completed_dps = dps.filter(is_completed=True).count()
            return (completed_dps / dps.count() * 100)
        else:  # BIG
            # For BIGs, calculate based on MTG completion
            mtgs = obj.children.all()
            if not mtgs.exists():
                return 0
            mtg_percentages = [self.get_completion_percentage(mtg) for mtg in mtgs]
            return sum(mtg_percentages) / len(mtg_percentages)

    def validate(self, data):
        # Validate goal hierarchy
        goal_type = data.get('goal_type')
        parent = data.get('parent')

        if goal_type == 'BIG' and parent is not None:
            raise serializers.ValidationError({
                'parent': 'BIG goals cannot have a parent goal.'
            })
        if goal_type == 'MTG':
            if parent is None:
                raise serializers.ValidationError({
                    'parent': 'MTG goals must have a BIG goal as parent.'
                })
            if parent.goal_type != 'BIG':
                raise serializers.ValidationError({
                    'parent': 'MTG goals must have a BIG goal as parent.'
                })
        if goal_type == 'DP':
            if parent is None:
                raise serializers.ValidationError({
                    'parent': 'DP goals must have a MTG goal as parent.'
                })
            if parent.goal_type != 'MTG':
                raise serializers.ValidationError({
                    'parent': 'DP goals must have a MTG goal as parent.'
                })

        # Validate dates
        if data.get('start_date') and data.get('target_date'):
            if data['start_date'] > data['target_date']:
                raise serializers.ValidationError({
                    'target_date': 'Target date must be after start date.'
                })

        return data

class DailyProgressSerializer(serializers.ModelSerializer):
    standard_progress = serializers.SerializerMethodField()
    process_progress = serializers.SerializerMethodField()

    class Meta:
        model = DailyProgress
        fields = ('id', 'date', 'standard_progress', 'process_progress')
        read_only_fields = ('id',)

    def get_standard_progress(self, obj):
        from standards.serializers import StandardProgressSerializer
        return StandardProgressSerializer(obj.standard_progress.all(), many=True).data

    def get_process_progress(self, obj):
        return ProcessProgressSerializer(obj.process_progress.all(), many=True).data

class ProcessProgressSerializer(serializers.ModelSerializer):
    process_title = serializers.CharField(source='process.title', read_only=True)
    category = serializers.CharField(source='process.category', read_only=True)
    parent_goal = serializers.CharField(source='process.parent.title', read_only=True)

    class Meta:
        model = ProcessProgress
        fields = (
            'id', 'daily_progress', 'process', 'process_title', 'category',
            'parent_goal', 'is_completed', 'time_spent_minutes', 'completion_time', 'notes'
        )
        read_only_fields = ('id', 'process_title', 'category', 'parent_goal', 'daily_progress', 'process')

    def validate(self, data):
        # Only validate process field if it's being updated
        if 'process' in data:
            # Ensure the process is a DP
            if data['process'].goal_type != 'DP':
                raise serializers.ValidationError({
                    'process': 'Process progress can only be tracked for Daily Process goals.'
                })
            
            # Ensure the process belongs to the current user
            if data['process'].user != self.context['request'].user:
                raise serializers.ValidationError({
                    'process': 'Invalid process selected.'
                })
        
        return data

class ReflectionSerializer(serializers.ModelSerializer):
    highlights = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        default=list
    )
    challenges = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        default=list
    )
    action_items = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        default=list
    )

    class Meta:
        model = Reflection
        fields = (
            'id', 'reflection_type', 'start_date', 'end_date', 'content',
            'highlights', 'challenges', 'action_items', 'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'created_at', 'updated_at')

    def validate(self, data):
        if data['start_date'] > data['end_date']:
            raise serializers.ValidationError({
                'end_date': 'End date must be after start date.'
            })
        
        # Validate reflection period based on type
        delta = data['end_date'] - data['start_date']
        if data['reflection_type'] == 'weekly' and delta.days != 6:
            raise serializers.ValidationError({
                'end_date': 'Weekly reflection must cover exactly 7 days.'
            })
        elif data['reflection_type'] == 'monthly' and delta.days not in [27, 28, 29, 30]:
            raise serializers.ValidationError({
                'end_date': 'Monthly reflection must cover one calendar month.'
            })
        elif data['reflection_type'] == 'quarterly' and delta.days not in [89, 90, 91, 92]:
            raise serializers.ValidationError({
                'end_date': 'Quarterly reflection must cover three calendar months.'
            })
        elif data['reflection_type'] == 'yearly' and delta.days not in [364, 365]:
            raise serializers.ValidationError({
                'end_date': 'Yearly reflection must cover one calendar year.'
            })
        
        return data
