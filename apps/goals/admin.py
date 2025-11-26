from django.contrib import admin
from .models import Goal, Achievement, UserAchievement


@admin.register(Goal)
class GoalAdmin(admin.ModelAdmin):
    list_display = ['user', 'title', 'goal_type', 'status', 'progress_percentage', 'target_date']
    list_filter = ['goal_type', 'status']
    search_fields = ['user__username', 'title']


@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'points']
    list_filter = ['category']
    search_fields = ['name']


@admin.register(UserAchievement)
class UserAchievementAdmin(admin.ModelAdmin):
    list_display = ['user', 'achievement', 'earned_at']
    list_filter = ['earned_at']
    search_fields = ['user__username', 'achievement__name']
