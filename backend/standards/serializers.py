from rest_framework import serializers
from .models import StandardCategory, Standard, StandardProgress

class StandardCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = StandardCategory
        fields = ('id', 'name', 'description', 'is_default', 'order', 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')

    def validate_name(self, value):
        user = self.context['request'].user
        if StandardCategory.objects.filter(user=user, name=value).exists():
            if self.instance and self.instance.name == value:
                return value
            raise serializers.ValidationError("A category with this name already exists.")
        return value

class StandardSerializer(serializers.ModelSerializer):
    success_criteria = serializers.ListField(
        child=serializers.CharField(max_length=500),
        required=False,
        default=list
    )
    specific_days = serializers.ListField(
        child=serializers.IntegerField(min_value=0, max_value=6),
        required=False,
        allow_null=True
    )
    category = StandardCategorySerializer(read_only=True)
    category_id = serializers.UUIDField(write_only=True)

    class Meta:
        model = Standard
        fields = (
            'id', 'category', 'category_id', 'title', 'description', 'minimum_requirement',
            'success_criteria', 'frequency', 'specific_days', 'time_of_day',
            'duration_minutes', 'is_active', 'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'created_at', 'updated_at')

    def validate(self, data):
        if data.get('frequency') == 'custom' and not data.get('specific_days'):
            raise serializers.ValidationError({
                'specific_days': 'Specific days are required for custom frequency.'
            })
        return data

    def create(self, validated_data):
        category_id = validated_data.pop('category_id')
        try:
            category = StandardCategory.objects.get(id=category_id, user=self.context['request'].user)
        except StandardCategory.DoesNotExist:
            raise serializers.ValidationError({'category_id': 'Invalid category selected.'})
        validated_data['category'] = category
        return super().create(validated_data)

    def update(self, instance, validated_data):
        if 'category_id' in validated_data:
            category_id = validated_data.pop('category_id')
            try:
                category = StandardCategory.objects.get(id=category_id, user=self.context['request'].user)
            except StandardCategory.DoesNotExist:
                raise serializers.ValidationError({'category_id': 'Invalid category selected.'})
            validated_data['category'] = category
        return super().update(instance, validated_data)

class StandardProgressSerializer(serializers.ModelSerializer):
    standard_title = serializers.CharField(source='standard.title', read_only=True)
    category_name = serializers.CharField(source='standard.category.name', read_only=True)
    frequency = serializers.CharField(source='standard.frequency', read_only=True)

    class Meta:
        model = StandardProgress
        fields = (
            'id', 'daily_progress', 'standard', 'standard_title', 'category_name',
            'frequency', 'is_completed', 'completion_time', 'notes'
        )
        read_only_fields = ('id', 'standard_title', 'category_name', 'frequency')

    def validate(self, data):
        # Only validate standard if it's being updated
        if 'standard' in data:
            # Ensure the standard belongs to the current user
            if data['standard'].user != self.context['request'].user:
                raise serializers.ValidationError({
                    'standard': 'Invalid standard selected.'
                })
        return data
