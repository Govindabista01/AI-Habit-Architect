import os
import sys
from django.apps import AppConfig
from django.conf import settings

class PredictionsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'predictions'
    predictor = None

    def ready(self):
        # Only load the predictor if we are not in the main thread (to avoid double loading during runserver)
        if os.environ.get('RUN_MAIN') == 'true':
            # Add ml_models to path
            ml_models_path = os.path.abspath(os.path.join(settings.BASE_DIR, '..', 'ml_models'))
            if ml_models_path not in sys.path:
                sys.path.insert(0, ml_models_path)
            
            try:
                from prediction import HabitPredictor
                PredictionsConfig.predictor = HabitPredictor()
                print("AI Habit Predictor loaded successfully on startup.")
            except Exception as e:
                print(f"Warning: AI Habit Predictor failed to load on startup: {e}")
