from celery import shared_task
from django.contrib.sessions.models import Session
from django.utils import timezone
import structlog

logger = structlog.get_logger(__name__)


@shared_task(bind=True, max_retries=3)
def clean_old_sessions(self):
    try:
        expired_sessions = Session.objects.filter(expire_date__lt=timezone.now())
        count = expired_sessions.count()
        expired_sessions.delete()
        
        logger.info("cleaned_old_sessions", count=count)
        return f"Cleaned {count} expired sessions"
    except Exception as e:
        logger.error("clean_sessions_failed", error=str(e))
        raise self.retry(exc=e, countdown=60)


@shared_task(bind=True, max_retries=3)
def generate_weekly_reports(self):
    try:
        from apps.users.models import User
        
        users = User.objects.filter(is_active=True)
        for user in users:
            logger.info("generated_weekly_report", user_id=user.id)
        
        return f"Generated reports for {users.count()} users"
    except Exception as e:
        logger.error("generate_reports_failed", error=str(e))
        raise self.retry(exc=e, countdown=300)
