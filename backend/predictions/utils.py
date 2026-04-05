import threading
from django.core.management import call_command
from django.utils import timezone
from datetime import timedelta
from habits.models import HabitRecord
from .models import ModelMetadata
from .apps import PredictionsConfig

def run_retraining():
    """Background task to run the management command and reload the model"""
    try:
        print("Starting automated AI background retraining...")
        call_command('retrain_ai_model')
        
        # Reload the predictor in memory after training completes
        from prediction import HabitPredictor
        PredictionsConfig.predictor = HabitPredictor()
        print("Automated AI retraining complete and model reloaded.")
    except Exception as e:
        print(f"Error during automated retraining: {e}")

def retrain_if_needed():
    """Check if the model is stale and trigger background retraining if so"""
    try:
        # 1. Get latest metadata
        try:
            latest = ModelMetadata.objects.latest()
            last_count = latest.record_count_at_training
            last_time = latest.last_trained_at
        except ModelMetadata.DoesNotExist:
            # If no training has ever happened, we should trigger one
            last_count = 0
            last_time = timezone.now() - timedelta(days=365)
            
        # 2. Get current record count
        current_count = HabitRecord.objects.count()
        
        # 3. Define thresholds (50 new records or 7 days old)
        new_records_threshold = 50
        time_threshold = timedelta(days=7)
        
        should_retrain = (
            (current_count - last_count >= new_records_threshold) or
            (timezone.now() - last_time >= time_threshold)
        )
        
        if should_retrain:
            # Prevent multiple simultaneous training threads
            # A simple way is to check if a thread named 'AI_Retrainer' is already running
            for thread in threading.enumerate():
                if thread.name == 'AI_Retrainer':
                    return
            
            # Start background thread
            thread = threading.Thread(target=run_retraining, name='AI_Retrainer')
            thread.daemon = True
            thread.start()
            
    except Exception as e:
        print(f"Error checking retraining status: {e}")
