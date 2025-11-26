from celery import shared_task
from datetime import datetime, timedelta
from django.utils import timezone
import structlog

from apps.users.models import User

logger = structlog.get_logger(__name__)


@shared_task(bind=True, max_retries=3)
def send_daily_reminders(self):
    try:
        from .bot import bot
        import asyncio
        
        users = User.objects.filter(
            is_active=True,
            telegram_id__isnull=False,
            profile__notifications_enabled=True
        )
        
        sent = 0
        for user in users:
            try:
                message = (
                    f"🌅 Доброе утро, {user.telegram_first_name or user.username}!\n\n"
                    "Не забудьте записать завтрак и выпить воды! 💧\n\n"
                    "Используйте /menu для начала."
                )
                
                asyncio.run(
                    bot.send_message(chat_id=user.telegram_id, text=message)
                )
                sent += 1
            except Exception as e:
                logger.error("failed_to_send_reminder", user_id=user.id, error=str(e))
        
        logger.info("daily_reminders_sent", sent=sent, total=users.count())
        
        return f"Sent {sent} reminders"
    except Exception as e:
        logger.error("send_reminders_failed", error=str(e))
        raise self.retry(exc=e, countdown=300)


@shared_task
def send_achievement_notification(user_id: int, achievement_name: str):
    try:
        from .bot import bot
        import asyncio
        
        user = User.objects.get(id=user_id, telegram_id__isnull=False)
        
        message = (
            f"🏆 Поздравляем!\n\n"
            f"Вы получили достижение: {achievement_name}!"
        )
        
        asyncio.run(
            bot.send_message(chat_id=user.telegram_id, text=message)
        )
        
        logger.info("achievement_notification_sent", user_id=user_id)
    except Exception as e:
        logger.error("failed_to_send_achievement", user_id=user_id, error=str(e))
