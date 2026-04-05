from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta
from habits.models import Habit, HabitRecord
from predictions.models import Prediction
import json


@login_required
def analytics_dashboard(request):
    """Main analytics dashboard"""
    user = request.user
    habits = Habit.objects.filter(user=user, is_active=True)
    
    # Date ranges
    today = timezone.now().date()
    thirty_days_ago = today - timedelta(days=30)
    seven_days_ago = today - timedelta(days=7)
    
    # Overall Statistics
    total_habits = habits.count()
    total_completions = sum(habit.total_completions for habit in habits)
    active_streaks = habits.filter(current_streak__gt=0).count()
    longest_streak = max([habit.longest_streak for habit in habits]) if habits.exists() else 0
    
    # 30-day completion rate
    all_records_30_days = HabitRecord.objects.filter(
        habit__user=user,
        date__gte=thirty_days_ago
    )
    total_records = all_records_30_days.count()
    completed_records = all_records_30_days.filter(completed=True).count()
    completion_rate_30 = int((completed_records / total_records * 100)) if total_records > 0 else 0
    
    # Last 7 days data for line chart
    last_7_days_data = []
    last_7_days_labels = []
    
    for i in range(6, -1, -1):
        date = today - timedelta(days=i)
        completed = HabitRecord.objects.filter(
            habit__user=user,
            date=date,
            completed=True
        ).count()
        
        last_7_days_data.append(completed)
        last_7_days_labels.append(date.strftime('%a'))
    
    # Category breakdown (pie chart data)
    category_data = {}
    for habit in habits:
        category = habit.get_category_display()
        category_data[category] = category_data.get(category, 0) + 1
    
    category_labels = list(category_data.keys())
    category_values = list(category_data.values())
    
    # Habit completion heatmap (last 30 days)
    heatmap_data = []
    for i in range(29, -1, -1):
        date = today - timedelta(days=i)
        completed = HabitRecord.objects.filter(
            habit__user=user,
            date=date,
            completed=True
        ).count()
        total_habits_that_day = habits.count()
        percentage = int((completed / total_habits_that_day * 100)) if total_habits_that_day > 0 else 0
        
        heatmap_data.append({
            'date': date.strftime('%Y-%m-%d'),
            'day': date.strftime('%d'),
            'month': date.strftime('%b'),
            'percentage': percentage,
            'completed': completed,
            'total': total_habits_that_day
        })
    
    # Best performing habits
    best_habits = []
    for habit in habits:
        rate = habit.get_completion_rate_30_days()
        best_habits.append({
            'name': habit.name,
            'rate': rate,
            'streak': habit.current_streak
        })
    best_habits.sort(key=lambda x: x['rate'], reverse=True)
    best_habits = best_habits[:5]
    
    # Struggling habits
    struggling_habits = []
    for habit in habits:
        rate = habit.get_completion_rate_30_days()
        if rate < 0.5:  # Changed from 50 to 0.5 (50%)
            struggling_habits.append({
                'name': habit.name,
                'rate': rate,
                'id': habit.id
            })
    struggling_habits.sort(key=lambda x: x['rate'])
    struggling_habits = struggling_habits[:5]
    
    # Recent predictions
    recent_predictions = Prediction.objects.filter(
        habit__user=user
    ).select_related('habit', 'recommendation').order_by('-created_at')[:5]
    
    context = {
        'total_habits': total_habits,
        'total_completions': total_completions,
        'active_streaks': active_streaks,
        'longest_streak': longest_streak,
        'completion_rate_30': completion_rate_30,
        
        # Chart data (let json_script handle serialization)
        'last_7_days_labels': last_7_days_labels,
        'last_7_days_data': last_7_days_data,
        'category_labels': category_labels,
        'category_values': category_values,
        
        'heatmap_data': heatmap_data,
        'best_habits': best_habits,
        'struggling_habits': struggling_habits,
        'recent_predictions': recent_predictions,
    }
    
    return render(request, 'analytics/dashboard.html', context)


@login_required
def habit_analytics(request, habit_id):
    """Analytics for a single habit"""
    from django.shortcuts import get_object_or_404
    
    habit = get_object_or_404(Habit, id=habit_id, user=request.user)
    
    today = timezone.now().date()
    thirty_days_ago = today - timedelta(days=30)
    
    # Get last 30 days records
    records = habit.records.filter(date__gte=thirty_days_ago).order_by('date')
    
    # Prepare data for chart
    dates = []
    completed_values = []
    
    for i in range(29, -1, -1):
        date = today - timedelta(days=i)
        record = records.filter(date=date).first()
        
        dates.append(date.strftime('%m/%d'))
        completed_values.append(1 if record and record.completed else 0)
    
    # Statistics
    total_days = 30
    completed_days = sum(completed_values)
    completion_rate = int((completed_days / total_days * 100))
    
    context = {
        'habit': habit,
        'dates': dates,
        'completed_values': completed_values,
        'total_days': total_days,
        'completed_days': completed_days,
        'completion_rate': completion_rate,
    }
    
    return render(request, 'analytics/habit_analytics.html', context)