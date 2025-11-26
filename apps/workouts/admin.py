from django.contrib import admin
from .models import Workout, WorkoutLog


@admin.register(Workout)
class WorkoutAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'calories_per_hour', 'is_public']
    list_filter = ['category', 'is_public']
    search_fields = ['name']


@admin.register(WorkoutLog)
class WorkoutLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'workout', 'date', 'duration_minutes', 'calories_burned']
    list_filter = ['date']
    search_fields = ['user__username', 'workout__name']
