import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('lifemetrics')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'calculate-daily-summaries': {
        'task': 'apps.food.tasks.calculate_daily_summaries',
        'schedule': crontab(hour=0, minute=5),  # Every day at 00:05
    },
    'send-daily-reminders': {
        'task': 'apps.telegram_bot.tasks.send_daily_reminders',
        'schedule': crontab(hour=9, minute=0),  # Every day at 09:00
    },
    'check-goal-progress': {
        'task': 'apps.goals.tasks.check_goal_progress',
        'schedule': crontab(hour='*/6'),  # Every 6 hours
    },
    'clean-old-sessions': {
        'task': 'apps.core.tasks.clean_old_sessions',
        'schedule': crontab(hour=3, minute=0),  # Every day at 03:00
    },
    'generate-weekly-reports': {
        'task': 'apps.core.tasks.generate_weekly_reports',
        'schedule': crontab(day_of_week=1, hour=8, minute=0),  # Every Monday at 08:00
    },
}

@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
