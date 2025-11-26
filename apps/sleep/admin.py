from django.contrib import admin
from .models import SleepLog


@admin.register(SleepLog)
class SleepLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'date', 'duration_hours', 'quality']
    list_filter = ['date', 'quality']
    search_fields = ['user__username']
