from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('create/', views.create_habit_view, name='create_habit'),
    path('<int:habit_id>/', views.habit_detail_view, name='habit_detail'),
    path('<int:habit_id>/track/', views.track_habit_view, name='track_habit'),
    path('<int:habit_id>/delete/', views.delete_habit_view, name='delete_habit'),
    path('<int:habit_id>/edit/', views.edit_habit_view, name='edit_habit'),
]