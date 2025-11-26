from typing import List, Optional, Dict
from datetime import date, timedelta
from decimal import Decimal
from django.db.models import Sum, Q, Avg, Count
from django.core.cache import cache
import structlog

from .models import Food, FoodLog, DailySummary, WaterLog
from apps.users.models import User, UserProfile

logger = structlog.get_logger(__name__)


class FoodService:
    
    @staticmethod
    def search_foods(query: str, user: Optional[User] = None, limit: int = 20) -> List[Food]:
        cache_key = f"food_search:{query}:{user.id if user else 'public'}"
        cached = cache.get(cache_key)
        
        if cached:
            return cached
        
        q_filter = Q(name__icontains=query) | Q(brand__icontains=query)
        
        if user:
            q_filter &= Q(Q(created_by=user) | Q(is_public=True))
        else:
            q_filter &= Q(is_public=True)
        
        foods = Food.objects.filter(q_filter, is_deleted=False).order_by('-is_verified', 'name')[:limit]
        foods = list(foods)
        
        cache.set(cache_key, foods, 300)  # Cache for 5 minutes
        
        return foods
    
    @staticmethod
    def get_food_by_barcode(barcode: str) -> Optional[Food]:
        try:
            return Food.objects.get(barcode=barcode, is_deleted=False)
        except Food.DoesNotExist:
            return None


class FoodLogService:
    
    @staticmethod
    def log_food(
        user: User,
        food_id: int,
        serving_amount: Decimal,
        meal_type: str,
        log_date: date,
        notes: str = ""
    ) -> FoodLog:
        food = Food.objects.get(id=food_id)
        
        food_log = FoodLog.objects.create(
            user=user,
            food=food,
            date=log_date,
            meal_type=meal_type,
            serving_amount=serving_amount,
            notes=notes,
        )
        
        DailySummaryService.invalidate_summary_cache(user, log_date)
        
        logger.info(
            "food_logged",
            user_id=user.id,
            food_id=food_id,
            date=str(log_date),
            meal_type=meal_type,
        )
        
        return food_log
    
    @staticmethod
    def get_daily_logs(user: User, log_date: date) -> Dict[str, List[FoodLog]]:
        logs = FoodLog.objects.filter(user=user, date=log_date).select_related('food')
        
        grouped = {
            'breakfast': [],
            'lunch': [],
            'dinner': [],
            'snack': [],
        }
        
        for log in logs:
            grouped[log.meal_type].append(log)
        
        return grouped


class DailySummaryService:
    
    @staticmethod
    def get_or_create_summary(user: User, summary_date: date) -> DailySummary:
        summary, created = DailySummary.objects.get_or_create(
            user=user,
            date=summary_date,
            defaults=DailySummaryService._get_default_targets(user)
        )
        
        if created or DailySummaryService._needs_recalculation(summary):
            DailySummaryService.recalculate_summary(summary)
        
        return summary
    
    @staticmethod
    def _get_default_targets(user: User) -> Dict:
        try:
            profile = user.profile
            return {
                'target_calories': profile.daily_calorie_target,
                'target_protein': profile.daily_protein_target,
                'target_carbs': profile.daily_carbs_target,
                'target_fat': profile.daily_fat_target,
            }
        except UserProfile.DoesNotExist:
            return {}
    
    @staticmethod
    def _needs_recalculation(summary: DailySummary) -> bool:
        from django.utils import timezone
        return (timezone.now() - summary.updated_at).seconds > 300
    
    @staticmethod
    def recalculate_summary(summary: DailySummary) -> DailySummary:
        logs = FoodLog.objects.filter(user=summary.user, date=summary.date)
        
        totals = logs.aggregate(
            total_calories=Sum('calories'),
            total_protein=Sum('protein'),
            total_carbs=Sum('carbs'),
            total_fat=Sum('fat'),
        )
        
        summary.total_calories = totals['total_calories'] or 0
        summary.total_protein = totals['total_protein'] or 0
        summary.total_carbs = totals['total_carbs'] or 0
        summary.total_fat = totals['total_fat'] or 0
        
        for meal_type in ['breakfast', 'lunch', 'dinner', 'snack']:
            meal_logs = logs.filter(meal_type=meal_type)
            meal_calories = meal_logs.aggregate(Sum('calories'))['calories__sum'] or 0
            setattr(summary, f'{meal_type}_calories', meal_calories)
        
        water_logs = WaterLog.objects.filter(user=summary.user, date=summary.date)
        summary.water_intake_ml = water_logs.aggregate(Sum('amount_ml'))['amount_ml__sum'] or 0
        
        summary.save()
        
        logger.info(
            "summary_recalculated",
            user_id=summary.user.id,
            date=str(summary.date),
            total_calories=float(summary.total_calories),
        )
        
        return summary
    
    @staticmethod
    def invalidate_summary_cache(user: User, summary_date: date):
        cache_key = f"daily_summary:{user.id}:{summary_date}"
        cache.delete(cache_key)
    
    @staticmethod
    def get_period_stats(user: User, start_date: date, end_date: date) -> Dict:
        summaries = DailySummary.objects.filter(
            user=user,
            date__range=[start_date, end_date]
        )
        
        stats = summaries.aggregate(
            avg_calories=Avg('total_calories'),
            avg_protein=Avg('total_protein'),
            avg_carbs=Avg('total_carbs'),
            avg_fat=Avg('total_fat'),
            days_logged=Count('id'),
        )
        
        total_days = (end_date - start_date).days + 1
        adherence = (stats['days_logged'] / total_days * 100) if total_days > 0 else 0
        
        return {
            'avg_calories': float(stats['avg_calories'] or 0),
            'avg_protein': float(stats['avg_protein'] or 0),
            'avg_carbs': float(stats['avg_carbs'] or 0),
            'avg_fat': float(stats['avg_fat'] or 0),
            'days_logged': stats['days_logged'],
            'total_days': total_days,
            'adherence_percentage': round(adherence, 2),
        }


class WaterService:
    
    @staticmethod
    def log_water(user: User, amount_ml: int, log_date: date) -> WaterLog:
        water_log = WaterLog.objects.create(
            user=user,
            date=log_date,
            amount_ml=amount_ml,
        )
        
        summary = DailySummaryService.get_or_create_summary(user, log_date)
        summary.water_intake_ml += amount_ml
        summary.save()
        
        logger.info("water_logged", user_id=user.id, amount_ml=amount_ml)
        
        return water_log
    
    @staticmethod
    def get_daily_water_intake(user: User, log_date: date) -> int:
        total = WaterLog.objects.filter(
            user=user,
            date=log_date
        ).aggregate(Sum('amount_ml'))
        
        return total['amount_ml__sum'] or 0
