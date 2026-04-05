from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

class Habit(models.Model):
    CATEGORY_CHOICES = [
        ('health', 'Health & Fitness'),
        ('productivity', 'Productivity'),
        ('learning', 'Learning'),
        ('mindfulness', 'Mindfulness'),
        ('social', 'Social'),
        ('finance', 'Finance'),
        ('other', 'Other'),
    ]
    
    FREQUENCY_CHOICES = [
        (1, 'Once a week'),
        (2, 'Twice a week'),
        (3, 'Three times a week'),
        (4, 'Four times a week'),
        (5, 'Five times a week'),
        (6, 'Six times a week'),
        (7, 'Every day'),
    ]
    
    # Foreign Keys
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='habits')
    
    # Basic Information
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='other')
    
    # Habit Configuration
    frequency_per_week = models.IntegerField(choices=FREQUENCY_CHOICES, default=7)
    motivation_score = models.IntegerField(default=5, help_text="Scale 1-10")
    difficulty_level = models.IntegerField(default=5, help_text="Scale 1-10")
    
    # Tracking Data
    current_streak = models.IntegerField(default=0)
    longest_streak = models.IntegerField(default=0)
    total_completions = models.IntegerField(default=0)
    
    # Status
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'habits'
        ordering = ['-created_at']
        verbose_name = 'Habit'
        verbose_name_plural = 'Habits'
    
    def __str__(self):
        return f"{self.user.username} - {self.name}"
    
    # Helper Methods for ML Features
    def get_completed_last_7_days(self):
        """Count completed days in last 7 days"""
        seven_days_ago = timezone.now().date() - timedelta(days=7)
        return self.records.filter(
            date__gte=seven_days_ago,
            completed=True
        ).count()
    
    def get_missed_last_7_days(self):
        """Count missed days in last 7 days"""
        return 7 - self.get_completed_last_7_days()
    
    def get_completion_rate_30_days(self):
        """Calculate success rate based on the current Calendar Month (Fresh Start Logic)"""
        today = timezone.now().date()
        start_of_month = today.replace(day=1) # The 1st of this month
        
        # Fair denominator: Days passed since the 1st of the month 
        # (or since creation if created this month)
        actual_start = max(start_of_month, self.created_at.date())
        denominator = (today - actual_start).days + 1
        
        completed_records = self.records.filter(
            date__gte=actual_start,
            completed=True
        ).count()
        return round(completed_records / denominator, 2)
    
    def was_completed_yesterday(self):
        """Check if habit was completed yesterday"""
        yesterday = timezone.now().date() - timedelta(days=1)
        return self.records.filter(date=yesterday, completed=True).exists()
    
    def update_streak(self):
        """Update current and longest streak"""
        today = timezone.now().date()
        yesterday = today - timedelta(days=1)
        
        completed_today = self.records.filter(date=today, completed=True).exists()
        completed_yesterday = self.records.filter(date=yesterday, completed=True).exists()
        
        if completed_today:
            if completed_yesterday:
                self.current_streak += 1
            else:
                self.current_streak = 1
        elif not completed_yesterday:
            self.current_streak = 0
        
        if self.current_streak > self.longest_streak:
            self.longest_streak = self.current_streak
        
        self.save()


class HabitRecord(models.Model):
    habit = models.ForeignKey(Habit, on_delete=models.CASCADE, related_name='records')
    date = models.DateField(default=timezone.now)
    completed = models.BooleanField(default=False)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'habit_records'
        unique_together = ['habit', 'date']
        ordering = ['-date']
        verbose_name = 'Habit Record'
        verbose_name_plural = 'Habit Records'
    
    def __str__(self):
        status = "✓" if self.completed else "✗"
        return f"{self.habit.name} - {self.date} {status}"