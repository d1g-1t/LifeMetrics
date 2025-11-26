from celery import shared_task
from datetime import date
import structlog

from apps.users.models import User
from .models import Goal

logger = structlog.get_logger(__name__)


@shared_task(bind=True, max_retries=3)
def check_goal_progress(self):
    try:
        active_goals = Goal.objects.filter(status='active')
        
        updated = 0
        completed = 0
        
        for goal in active_goals:
            
            if goal.current_value >= goal.target_value:
                goal.status = 'completed'
                goal.completed_date = date.today()
                goal.save()
                completed += 1
            
            updated += 1
        
        logger.info("goal_progress_checked", updated=updated, completed=completed)
        
        return f"Checked {updated} goals, {completed} completed"
    except Exception as e:
        logger.error("check_goal_progress_failed", error=str(e))
        raise self.retry(exc=e, countdown=300)
