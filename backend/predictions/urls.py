from django.urls import path
from . import views

urlpatterns = [
    path('predict/<int:habit_id>/', views.predict_habit_view, name='predict_habit'),
    path('history/', views.prediction_history_view, name='prediction_history'),
]