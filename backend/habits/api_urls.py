from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import HabitViewSet, dashboard_stats, prediction_history

router = DefaultRouter()
router.register(r'habits', HabitViewSet, basename='habit')

urlpatterns = [
    path('', include(router.urls)),
    path('dashboard/', dashboard_stats, name='api-dashboard'),
    path('predictions/', prediction_history, name='api-predictions'),
]