from rest_framework import serializers
from .models import Habit, HabitRecord
from predictions.models import Prediction, Recommendation
from django.contrib.auth.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']


class HabitSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    frequency_display = serializers.CharField(source='get_frequency_per_week_display', read_only=True)
    
    # Computed fields
    completed_last_7 = serializers.SerializerMethodField()
    missed_last_7 = serializers.SerializerMethodField()
    completion_rate_30 = serializers.SerializerMethodField()
    
    class Meta:
        model = Habit
        fields = [
            'id', 'user', 'name', 'description', 'category', 'category_display',
            'frequency_per_week', 'frequency_display', 'motivation_score',
            'difficulty_level', 'current_streak', 'longest_streak',
            'total_completions', 'is_active', 'created_at', 'updated_at',
            'completed_last_7', 'missed_last_7', 'completion_rate_30'
        ]
        read_only_fields = ['id', 'user', 'current_streak', 'longest_streak', 
                           'total_completions', 'created_at', 'updated_at']
    
    def get_completed_last_7(self, obj):
        return obj.get_completed_last_7_days()
    
    def get_missed_last_7(self, obj):
        return obj.get_missed_last_7_days()
    
    def get_completion_rate_30(self, obj):
        return obj.get_completion_rate_30_days()


class HabitRecordSerializer(serializers.ModelSerializer):
    habit_name = serializers.CharField(source='habit.name', read_only=True)
    
    class Meta:
        model = HabitRecord
        fields = ['id', 'habit', 'habit_name', 'date', 'completed', 'notes', 'created_at']
        read_only_fields = ['id', 'created_at']


class RecommendationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recommendation
        fields = ['id', 'message', 'tips', 'risk_level', 'created_at']


class PredictionSerializer(serializers.ModelSerializer):
    habit_name = serializers.CharField(source='habit.name', read_only=True)
    recommendation = RecommendationSerializer(read_only=True)
    
    class Meta:
        model = Prediction
        fields = [
            'id', 'habit', 'habit_name', 'prediction_date',
            'will_complete', 'completion_probability', 'confidence_level',
            'recommendation', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class HabitCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Habit
        fields = [
            'name', 'description', 'category', 'frequency_per_week',
            'motivation_score', 'difficulty_level'
        ]
    
    def validate_motivation_score(self, value):
        if value < 1 or value > 10:
            raise serializers.ValidationError("Motivation score must be between 1 and 10")
        return value
    
    def validate_difficulty_level(self, value):
        if value < 1 or value > 10:
            raise serializers.ValidationError("Difficulty level must be between 1 and 10")
        return value