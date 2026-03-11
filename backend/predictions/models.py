from django.db import models
from django.utils import timezone
from habits.models import Habit

class Prediction(models.Model):
    habit = models.ForeignKey(Habit, on_delete=models.CASCADE, related_name='predictions')
    prediction_date = models.DateField(default=timezone.now)
    
    # Prediction Results
    will_complete = models.BooleanField()
    completion_probability = models.FloatField()
    confidence_level = models.CharField(max_length=20)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'predictions'
        ordering = ['-prediction_date', '-created_at']
        verbose_name = 'Prediction'
        verbose_name_plural = 'Predictions'
    
    def __str__(self):
        return f"Prediction for {self.habit.name} on {self.prediction_date}"


class Recommendation(models.Model):
    prediction = models.OneToOneField(Prediction, on_delete=models.CASCADE, related_name='recommendation')
    
    # Recommendation Content
    message = models.TextField()
    tips = models.JSONField()  # List of recommendation tips
    risk_level = models.CharField(max_length=20)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'recommendations'
        ordering = ['-created_at']
        verbose_name = 'Recommendation'
        verbose_name_plural = 'Recommendations'
    
    def __str__(self):
        return f"Recommendation for {self.prediction.habit.name}"