import random
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from habits.models import Habit, HabitRecord

class Command(BaseCommand):
    help = 'Generates dummy habit records to test the AI model'

    def handle(self, *args, **options):
        self.stdout.write("Generating dummy data...")

        # 1. Get or create a test user
        user, created = User.objects.get_or_create(
            username='test_ai_user',
            defaults={'email': 'test@example.com'}
        )
        if created:
            user.set_password('password123')
            user.save()
            self.stdout.write(f"Created test user: {user.username}")

        # 2. Create sample habits
        habits_data = [
            {'name': 'Morning Jog', 'category': 'health', 'freq': 5, 'mot': 8, 'diff': 7},
            {'name': 'Read 10 Pages', 'category': 'learning', 'freq': 7, 'mot': 6, 'diff': 4},
            {'name': 'No Spend Day', 'category': 'finance', 'freq': 7, 'mot': 9, 'diff': 6},
        ]
        
        habits = []
        for data in habits_data:
            habit, _ = Habit.objects.get_or_create(
                user=user,
                name=data['name'],
                defaults={
                    'category': data['category'],
                    'frequency_per_week': data['freq'],
                    'motivation_score': data['mot'],
                    'difficulty_level': data['diff']
                }
            )
            habits.append(habit)

        # 3. Generate 30 days of history for each habit
        today = timezone.now().date()
        records_created = 0
        
        for habit in habits:
            # We want a mix of True and False to ensure the AI learns correctly.
            # A base 70% chance of completion ensures the dataset has both classes.
            completion_chance = 0.7 
            
            for days_ago in range(30, 0, -1):
                record_date = today - timedelta(days=days_ago)
                
                # Check if a record already exists on this date to prevent unique constraint errors
                if not HabitRecord.objects.filter(habit=habit, date=record_date).exists():
                    is_completed = random.random() < completion_chance
                    
                    HabitRecord.objects.create(
                        habit=habit,
                        date=record_date,
                        completed=is_completed,
                        notes="Auto-generated dummy data"
                    )
                    records_created += 1

        self.stdout.write(self.style.SUCCESS(f"Successfully generated {records_created} new dummy records!"))
        self.stdout.write(self.style.SUCCESS("You now have enough data to train the model."))
        self.stdout.write("Run: python manage.py retrain_ai_model")
