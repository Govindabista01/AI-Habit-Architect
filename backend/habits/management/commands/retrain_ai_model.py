import sys
import os
import pandas as pd
from datetime import timedelta
from itertools import groupby

from django.core.management.base import BaseCommand
from django.conf import settings
from habits.models import Habit, HabitRecord
from predictions.models import ModelMetadata

# Append ml_models to python path
ml_models_path = os.path.abspath(os.path.join(settings.BASE_DIR, '..', 'ml_models'))
if ml_models_path not in sys.path:
    sys.path.insert(0, ml_models_path)

from preprocess_data import DataPreprocessor
from train_model import ModelTrainer

class Command(BaseCommand):
    help = 'Retrain the AI prediction model using live database data'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Starting AI Model Retraining Process..."))
        
        # 1. Fetch data
        records = list(HabitRecord.objects.select_related('habit').order_by('habit_id', 'date'))
        
        if len(records) < 50:
            self.stdout.write(self.style.ERROR(f"Only {len(records)} records found. At least 50 are required to train the model cleanly. Aborting."))
            return
            
        self.stdout.write(f"Generating historical data for {len(records)} records...")
        
        dataset = []
        
        # Group records by habit
        for habit_id, habit_records_iter in groupby(records, key=lambda x: x.habit.id):
            habit_records = list(habit_records_iter)
            habit = habit_records[0].habit
            
            # Map of date -> completed status
            date_map = {r.date: r.completed for r in habit_records}
            
            for current_record in habit_records:
                current_date = current_record.date
                
                # Previous day
                prev_date = current_date - timedelta(days=1)
                previous_day_completed = 1 if date_map.get(prev_date, False) else 0
                
                # Last 7 days
                completed_7 = sum(1 for d in range(1, 8) if date_map.get(current_date - timedelta(days=d), False))
                missed_7 = 7 - completed_7
                
                # Last 30 days
                records_in_30 = [r for r in habit_records if prev_date >= r.date >= current_date - timedelta(days=30)]
                total_in_30 = len(records_in_30)
                completed_in_30 = sum(1 for r in records_in_30 if r.completed)
                
                completion_rate_30 = round(completed_in_30 / total_in_30, 2) if total_in_30 > 0 else 0.0
                
                # Streak (consecutive days before current_date)
                streak = 0
                check_date = prev_date
                while date_map.get(check_date, False):
                    streak += 1
                    check_date -= timedelta(days=1)
                
                dataset.append({
                    'habit_category': habit.category,
                    'habit_frequency_per_week': habit.frequency_per_week,
                    'streak_length': streak,
                    'completed_days_last_7': completed_7,
                    'missed_days_last_7': missed_7,
                    'completion_rate_last_30': completion_rate_30,
                    'previous_day_completed': previous_day_completed,
                    'motivation_score': habit.motivation_score,
                    'habit_difficulty': habit.difficulty_level,
                    'day_of_week': current_date.weekday(),  # 0=Monday, 6=Sunday
                    'is_weekend': 1 if current_date.weekday() >= 5 else 0,
                    'habit_completed_today': 1 if current_record.completed else 0
                })

        df = pd.DataFrame(dataset)
        
        # Ensure we have both successful and failed habits to train on
        if len(df['habit_completed_today'].unique()) < 2:
            self.stdout.write(self.style.ERROR("Dataset only contains one class (all completions or all failures). Cannot train model until there is varied data. Aborting."))
            return

        self.stdout.write(self.style.SUCCESS(f"Generated DataFrame with {df.shape[0]} rows and {df.shape[1]} columns"))
        
        # 2. Preprocess Data
        preprocessor = DataPreprocessor(dataframe=df)
        
        # Redirect stdout temporarily or just let it print
        processed_data = preprocessor.run_pipeline()
        
        if processed_data is None:
            self.stdout.write(self.style.ERROR("Preprocessing failed."))
            return
            
        # 3. Train Model
        trainer = ModelTrainer()
        trainer.train(processed_data['X_train'], processed_data['y_train'])
        
        # 4. Evaluate & Save
        results = trainer.evaluate(processed_data['X_test'], processed_data['y_test'])
        trainer.save_model()
        trainer.summary(results)
        
        # 5. Log training metadata
        ModelMetadata.objects.create(
            record_count_at_training=len(records),
            accuracy_achieved=results.get('accuracy', 0.0)
        )
        
        self.stdout.write(self.style.SUCCESS("\nModel successfully retrained and metadata logged!"))
