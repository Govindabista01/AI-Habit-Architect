from django.contrib import admin
from .models import Prediction, Recommendation

@admin.register(Prediction)
class PredictionAdmin(admin.ModelAdmin):
    list_display = ['habit', 'prediction_date', 'will_complete', 'completion_probability', 'confidence_level']
    list_filter = ['will_complete', 'confidence_level', 'prediction_date']
    search_fields = ['habit__name', 'habit__user__username']
    readonly_fields = ['created_at']
    date_hierarchy = 'prediction_date'

@admin.register(Recommendation)
class RecommendationAdmin(admin.ModelAdmin):
    list_display = ['prediction', 'risk_level', 'created_at']
    list_filter = ['risk_level']
    search_fields = ['prediction__habit__name']
    readonly_fields = ['created_at']