from django.contrib import admin
from .models import Food, FoodLog, DailySummary, WaterLog


@admin.register(Food)
class FoodAdmin(admin.ModelAdmin):
    list_display = ['name', 'brand', 'calories', 'protein', 'carbs', 'fat', 'is_verified', 'is_public']
    list_filter = ['is_verified', 'is_public', 'is_deleted']
    search_fields = ['name', 'brand', 'barcode']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(FoodLog)
class FoodLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'food', 'date', 'meal_type', 'serving_amount', 'calories']
    list_filter = ['date', 'meal_type']
    search_fields = ['user__username', 'food__name']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(DailySummary)
class DailySummaryAdmin(admin.ModelAdmin):
    list_display = ['user', 'date', 'total_calories', 'target_calories', 'water_intake_ml']
    list_filter = ['date']
    search_fields = ['user__username']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(WaterLog)
class WaterLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'date', 'amount_ml', 'time']
    list_filter = ['date']
    search_fields = ['user__username']
    readonly_fields = ['created_at']
