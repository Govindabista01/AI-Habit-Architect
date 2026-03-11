from django.urls import path
from . import views

urlpatterns = [
    path('', views.analytics_dashboard, name='analytics_dashboard'),
    path('habit/<int:habit_id>/', views.habit_analytics, name='habit_analytics'),
]