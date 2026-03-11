from django.contrib import admin
from .models import Habit, HabitRecord

@admin.register(Habit)
class HabitAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'category', 'current_streak', 'is_active', 'created_at']
    list_filter = ['category', 'is_active', 'created_at']
    search_fields = ['name', 'user__username']
    readonly_fields = ['created_at', 'updated_at', 'total_completions', 'longest_streak']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'name', 'description', 'category')
        }),
        ('Configuration', {
            'fields': ('frequency_per_week', 'motivation_score', 'difficulty_level')
        }),
        ('Tracking', {
            'fields': ('current_streak', 'longest_streak', 'total_completions')
        }),
        ('Status', {
            'fields': ('is_active', 'created_at', 'updated_at')
        }),
    )

@admin.register(HabitRecord)
class HabitRecordAdmin(admin.ModelAdmin):
    list_display = ['habit', 'date', 'completed', 'created_at']
    list_filter = ['completed', 'date']
    search_fields = ['habit__name', 'habit__user__username']
    date_hierarchy = 'date'
    readonly_fields = ['created_at', 'updated_at']