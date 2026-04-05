import sys
import os
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from habits.models import Habit
from .apps import PredictionsConfig
from .models import Prediction, Recommendation
from .utils import retrain_if_needed

# Add ml_models folder to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'ml_models'))
from prediction import HabitPredictor


@login_required
def predict_habit_view(request, habit_id):
    """Get AI prediction for a specific habit"""
    habit = get_object_or_404(Habit, id=habit_id, user=request.user)

    # 1. Start background retraining if needed (doesn't block the request)
    retrain_if_needed()

    # 2. Prepare habit data for ML model
    habit_data = {
    'habit_name': habit.name,
    'habit_category': habit.category,
    'habit_frequency_per_week': habit.frequency_per_week,
    'streak_length': habit.current_streak,
    'completed_days_last_7': habit.get_completed_last_7_days(),
    'missed_days_last_7': habit.get_missed_last_7_days(),
    'completion_rate_last_30': habit.get_completion_rate_30_days(),
    'previous_day_completed': 1 if habit.was_completed_yesterday() else 0,
    'motivation_score': habit.motivation_score,
    'habit_difficulty': habit.difficulty_level
    }

    # Get prediction from ML model
    predictor = PredictionsConfig.predictor
    
    if predictor is None:
        # Fallback if model failed to load at startup
        from prediction import HabitPredictor
        predictor = HabitPredictor()
        
    prediction_result = predictor.predict(habit_data)

    # Don't save prediction if AI model wasn't loaded or returned an error
    if 'error' in prediction_result:
        messages.warning(request, f"Note: AI results are currently simulation-only. {prediction_result['error']}")
        recommendation_result = predictor.get_recommendation(prediction_result, habit_data)
        context = {
            'habit': habit,
            'prediction': prediction_result,
            'recommendation': recommendation_result,
            'habit_data': habit_data,
        }
        return render(request, 'predictions/predict.html', context)

    recommendation_result = predictor.get_recommendation(prediction_result, habit_data)

    # Only save prediction to database if the habit has been tracked at least once
    # This prevents the AI log from being cluttered with "empty" habit data
    if habit.records.exists():
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
    else:
        messages.info(request, "Note: Complete your first habit check-in to start saving AI predictions in your log.")

    context = {
        'habit': habit,
        'prediction': prediction_result,
        'recommendation': recommendation_result,
        'habit_data': habit_data,
    }

    return render(request, 'predictions/predict.html', context)


@login_required
def prediction_history_view(request):
    """Show all past predictions for the logged in user"""
    # Filter out entries with 'None' confidence_level (errors)
    # AND filter to only show predictions for habits that have been tracked
    predictions = Prediction.objects.filter(
        habit__user=request.user,
        habit__records__isnull=False
    ).exclude(
        confidence_level='None'
    ).select_related('habit', 'recommendation').distinct().order_by('-created_at')

    context = {
        'predictions': predictions,
    }

    return render(request, 'predictions/history.html', context)