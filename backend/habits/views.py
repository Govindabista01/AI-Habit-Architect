from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from .models import Habit, HabitRecord


@login_required
def dashboard_view(request):
    """Main dashboard page"""
    habits = request.user.habits.filter(is_active=True)
    today = timezone.now().date()

    # Count completed habits today
    completed_today = 0
    for habit in habits:
        if habit.records.filter(date=today, completed=True).exists():
            completed_today += 1

    total_habits = habits.count()

    # Calculate percentage
    if total_habits > 0:
        completion_percentage = int((completed_today / total_habits) * 100)
    else:
        completion_percentage = 0

    context = {
        'habits': habits,
        'completed_today': completed_today,
        'total_habits': total_habits,
        'completion_percentage': completion_percentage,
        'today': today,
    }

    return render(request, 'habits/dashboard.html', context)


@login_required
def create_habit_view(request):
    """Create a new habit"""

    if request.method == 'POST':
        name = request.POST.get('name')
        category = request.POST.get('category')
        description = request.POST.get('description', '')
        frequency = request.POST.get('frequency_per_week')
        motivation = request.POST.get('motivation_score')
        difficulty = request.POST.get('difficulty_level')

        # Validate fields
        if not name or not category or not frequency or not motivation or not difficulty:
            messages.error(request, 'Please fill all required fields.')
            return redirect('create_habit')

        # Create habit
        Habit.objects.create(
            user=request.user,
            name=name,
            category=category,
            description=description,
            frequency_per_week=int(frequency),
            motivation_score=int(motivation),
            difficulty_level=int(difficulty)
        )

        messages.success(request, f'Habit "{name}" created successfully.')
        return redirect('dashboard')

    return render(request, 'habits/create_habit.html')


@login_required
def habit_detail_view(request, habit_id):
    """View single habit with all details and records"""
    habit = get_object_or_404(Habit, id=habit_id, user=request.user)

    # Get last 30 days of records
    thirty_days_ago = timezone.now().date() - timedelta(days=30)
    records = habit.records.filter(date__gte=thirty_days_ago).order_by('-date')

    # Build a date-to-record map for the last 7 days
    today = timezone.now().date()
    last_7_days = []
    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        completed = habit.records.filter(date=day, completed=True).exists()
        last_7_days.append({
            'date': day,
            'day_name': day.strftime('%a'),
            'completed': completed
        })

    context = {
        'habit': habit,
        'records': records,
        'last_7_days': last_7_days,
        'completion_rate': habit.get_completion_rate_30_days(),
    }

    return render(request, 'habits/habit_detail.html', context)


@login_required
def track_habit_view(request, habit_id):
    """Mark habit as completed or uncompleted for today"""
    habit = get_object_or_404(Habit, id=habit_id, user=request.user)
    today = timezone.now().date()

    # Check if record exists for today
    record_exists = HabitRecord.objects.filter(habit=habit, date=today).exists()

    if record_exists:
        # Get existing record and toggle it
        record = HabitRecord.objects.get(habit=habit, date=today)
        record.completed = not record.completed
        record.save()

        if record.completed:
            habit.total_completions += 1
            messages.success(request, f'"{habit.name}" marked as completed.')
        else:
            habit.total_completions -= 1
            messages.warning(request, f'"{habit.name}" marked as not completed.')
        habit.save()
    else:
        # Create new record as completed
        HabitRecord.objects.create(
            habit=habit,
            date=today,
            completed=True
        )
        habit.total_completions += 1
        habit.save()
        messages.success(request, f'"{habit.name}" marked as completed.')

    # Update streak
    habit.update_streak()

    return redirect('dashboard')


@login_required
def delete_habit_view(request, habit_id):
    """Deactivate habit (soft delete)"""
    habit = get_object_or_404(Habit, id=habit_id, user=request.user)
    habit_name = habit.name
    habit.is_active = False
    habit.save()

    messages.success(request, f'Habit "{habit_name}" has been removed.')
    return redirect('dashboard')


@login_required
def edit_habit_view(request, habit_id):
    """Edit existing habit"""
    habit = get_object_or_404(Habit, id=habit_id, user=request.user)

    if request.method == 'POST':
        habit.name = request.POST.get('name', habit.name)
        habit.category = request.POST.get('category', habit.category)
        habit.description = request.POST.get('description', habit.description)
        habit.frequency_per_week = int(request.POST.get('frequency_per_week', habit.frequency_per_week))
        habit.motivation_score = int(request.POST.get('motivation_score', habit.motivation_score))
        habit.difficulty_level = int(request.POST.get('difficulty_level', habit.difficulty_level))
        habit.save()

        messages.success(request, f'Habit "{habit.name}" updated successfully.')
        return redirect('habit_detail', habit_id=habit.id)

    context = {
        'habit': habit,
    }

    return render(request, 'habits/edit_habit.html', context)