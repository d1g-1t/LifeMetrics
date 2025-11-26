from celery import shared_task
from datetime import date, timedelta
from django.utils import timezone
import structlog

from apps.users.models import User
from .services import DailySummaryService

logger = structlog.get_logger(__name__)


@shared_task(bind=True, max_retries=3)
def calculate_daily_summaries(self):
    try:
        yesterday = (timezone.now() - timedelta(days=1)).date()
        users = User.objects.filter(is_active=True)
        
        processed = 0
        for user in users:
            try:
                summary = DailySummaryService.get_or_create_summary(user, yesterday)
                DailySummaryService.recalculate_summary(summary)
                processed += 1
            except Exception as e:
                logger.error("failed_to_calculate_summary", user_id=user.id, error=str(e))
        
        logger.info("daily_summaries_calculated", processed=processed, total=users.count())
        
        return f"Calculated {processed} summaries"
    except Exception as e:
        logger.error("calculate_summaries_failed", error=str(e))
        raise self.retry(exc=e, countdown=300)


@shared_task(bind=True)
def recalculate_user_summary(self, user_id: int, summary_date: str):
    try:
        user = User.objects.get(id=user_id)
        parsed_date = date.fromisoformat(summary_date)
        
        summary = DailySummaryService.get_or_create_summary(user, parsed_date)
        DailySummaryService.recalculate_summary(summary)
        
        logger.info("user_summary_recalculated", user_id=user_id, date=summary_date)
        
        return f"Recalculated summary for user {user_id}"
    except Exception as e:
        logger.error("recalculate_summary_failed", user_id=user_id, error=str(e))
        raise
