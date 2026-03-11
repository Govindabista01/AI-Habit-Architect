from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.utils import timezone
from .models import Habit, HabitRecord
from predictions.models import Prediction, Recommendation
from .serializers import (
    HabitSerializer, HabitCreateSerializer, HabitRecordSerializer,
    PredictionSerializer
)
import sys
import os

# Import ML prediction engine
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'ml_models'))
from prediction import HabitPredictor


class HabitViewSet(viewsets.ModelViewSet):
    """
    API endpoint for habits
    
    list: Get all habits for logged in user
    create: Create new habit
    retrieve: Get single habit details
    update: Update habit
    destroy: Delete habit
    """
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Habit.objects.filter(user=self.request.user, is_active=True)
    
    def get_serializer_class(self):
        if self.action == 'create':
            return HabitCreateSerializer
        return HabitSerializer
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    def destroy(self, request, *args, **kwargs):
        habit = self.get_object()
        habit.is_active = False
        habit.save()
        return Response({'message': 'Habit deleted successfully'}, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'])
    def track(self, request, pk=None):
        """
        Track habit completion for today
        POST /api/habits/{id}/track/
        """
        habit = self.get_object()
        today = timezone.now().date()
        
        record, created = HabitRecord.objects.get_or_create(
            habit=habit,
            date=today,
            defaults={'completed': True}
        )
        
        if not created:
            record.completed = not record.completed
            record.save()
        
        if record.completed:
            habit.total_completions += 1 if created else 0
        else:
            habit.total_completions -= 1
        
        habit.save()
        habit.update_streak()
        
        return Response({
            'message': 'Habit tracked successfully',
            'completed': record.completed,
            'current_streak': habit.current_streak
        })
    
    @action(detail=True, methods=['get'])
    def predict(self, request, pk=None):
        """
        Get AI prediction for habit
        GET /api/habits/{id}/predict/
        """
        habit = self.get_object()
        
        # Prepare data for ML model
        habit_data = {
            'habit_frequency_per_week': habit.frequency_per_week,
            'streak_length': habit.current_streak,
            'completed_days_last_7': habit.get_completed_last_7_days(),
            'missed_days_last_7': habit.get_missed_last_7_days(),
            'completion_rate_last_30': habit.get_completion_rate_30_days(),
            'previous_day_completed': 1 if habit.was_completed_yesterday() else 0,
            'motivation_score': habit.motivation_score,
            'habit_difficulty': habit.difficulty_level
        }
        
        # Get prediction
        predictor = HabitPredictor()
        prediction_result = predictor.predict(habit_data)
        recommendation_result = predictor.get_recommendation(prediction_result, habit_data)
        
        # Save to database
        prediction_obj = Prediction.objects.create(
            habit=habit,
            will_complete=prediction_result['will_complete'],
            completion_probability=prediction_result['completion_probability'],
            confidence_level=prediction_result['confidence']
        )
        
        Recommendation.objects.create(
            prediction=prediction_obj,
            message=recommendation_result['message'],
            tips=recommendation_result['tips'],
            risk_level=recommendation_result['risk_level']
        )
        
        serializer = PredictionSerializer(prediction_obj)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def records(self, request, pk=None):
        """
        Get all records for a habit
        GET /api/habits/{id}/records/
        """
        habit = self.get_object()
        records = habit.records.all().order_by('-date')[:30]  # Last 30 records
        serializer = HabitRecordSerializer(records, many=True)
        return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_stats(request):
    """
    Get dashboard statistics
    GET /api/dashboard/
    """
    habits = Habit.objects.filter(user=request.user, is_active=True)
    today = timezone.now().date()
    
    completed_today = 0
    for habit in habits:
        if habit.records.filter(date=today, completed=True).exists():
            completed_today += 1
    
    total_habits = habits.count()
    completion_percentage = int((completed_today / total_habits * 100)) if total_habits > 0 else 0
    active_streaks = habits.filter(current_streak__gt=0).count()
    
    return Response({
        'total_habits': total_habits,
        'completed_today': completed_today,
        'completion_percentage': completion_percentage,
        'active_streaks': active_streaks
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def prediction_history(request):
    """
    Get all predictions for user
    GET /api/predictions/
    """
    predictions = Prediction.objects.filter(
        habit__user=request.user
    ).select_related('habit', 'recommendation').order_by('-created_at')[:20]
    
    serializer = PredictionSerializer(predictions, many=True)
    return Response(serializer.data)