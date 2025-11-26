from django.contrib import admin
from .models import User, UserProfile, TelegramSession


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['id', 'username', 'email', 'telegram_id', 'is_premium', 'created_at']
    list_filter = ['is_active', 'is_premium', 'created_at']
    search_fields = ['username', 'email', 'telegram_username', 'telegram_id']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'gender', 'age', 'height', 'weight', 'goal', 'daily_calorie_target']
    list_filter = ['gender', 'goal', 'activity_level']
    search_fields = ['user__username']
    readonly_fields = ['created_at', 'updated_at', 'bmr', 'tdee']


@admin.register(TelegramSession)
class TelegramSessionAdmin(admin.ModelAdmin):
    list_display = ['user', 'telegram_id', 'state', 'is_active', 'last_activity']
    list_filter = ['is_active', 'state']
    search_fields = ['user__username', 'telegram_id']
    readonly_fields = ['created_at', 'updated_at', 'last_activity']
