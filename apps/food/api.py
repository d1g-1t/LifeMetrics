from ninja import Router, Query
from django.shortcuts import get_object_or_404
from typing import List
from datetime import date, timedelta
import structlog

from .models import Food, FoodLog, DailySummary
from .schemas import (
    FoodSchema,
    FoodCreateSchema,
    FoodLogSchema,
    FoodLogCreateSchema,
    DailySummarySchema,
    WaterLogSchema,
    FoodSearchResultSchema,
    NutritionStatsSchema,
)
from .services import FoodService, FoodLogService, DailySummaryService, WaterService
from apps.core.auth import AuthBearer

router = Router()
logger = structlog.get_logger(__name__)


@router.get("/search", response=List[FoodSchema], auth=AuthBearer())
def search_foods(request, query: str = Query(..., min_length=2)):
    foods = FoodService.search_foods(query, request.auth)
    return foods


@router.get("/barcode/{barcode}", response=FoodSchema, auth=AuthBearer())
def get_food_by_barcode(request, barcode: str):
    food = FoodService.get_food_by_barcode(barcode)
    
    if not food:
        return router.create_response(
            request,
            {'error': 'Food not found'},
            status=404
        )
    
    return food


@router.post("/foods", response=FoodSchema, auth=AuthBearer())
def create_custom_food(request, data: FoodCreateSchema):
    food = Food.objects.create(
        created_by=request.auth,
        is_public=False,
        **data.dict()
    )
    
    logger.info("custom_food_created", user_id=request.auth.id, food_id=food.id)
    
    return food


@router.post("/log", response=FoodLogSchema, auth=AuthBearer())
def log_food(request, data: FoodLogCreateSchema):
    food_log = FoodLogService.log_food(
        user=request.auth,
        food_id=data.food_id,
        serving_amount=data.serving_amount,
        meal_type=data.meal_type,
        log_date=data.date,
        notes=data.notes or "",
    )
    
    return food_log


@router.get("/logs", response=List[FoodLogSchema], auth=AuthBearer())
def get_food_logs(request, date: date = Query(None)):
    log_date = date or date.today()
    logs = FoodLogService.get_daily_logs(request.auth, log_date)
    
    all_logs = []
    for meal_logs in logs.values():
        all_logs.extend(meal_logs)
    
    return all_logs


@router.delete("/logs/{log_id}", auth=AuthBearer())
def delete_food_log(request, log_id: int):
    log = get_object_or_404(FoodLog, id=log_id, user=request.auth)
    log_date = log.date
    log.delete()
    
    DailySummaryService.invalidate_summary_cache(request.auth, log_date)
    
    logger.info("food_log_deleted", user_id=request.auth.id, log_id=log_id)
    
    return {'success': True}


@router.get("/summary", response=DailySummarySchema, auth=AuthBearer())
def get_daily_summary(request, date: date = Query(None)):
    summary_date = date or date.today()
    summary = DailySummaryService.get_or_create_summary(request.auth, summary_date)
    
    return summary


@router.get("/stats/week", response=NutritionStatsSchema, auth=AuthBearer())
def get_weekly_stats(request):
    end_date = date.today()
    start_date = end_date - timedelta(days=6)
    
    stats = DailySummaryService.get_period_stats(request.auth, start_date, end_date)
    stats['period'] = 'week'
    
    return stats


@router.get("/stats/month", response=NutritionStatsSchema, auth=AuthBearer())
def get_monthly_stats(request):
    end_date = date.today()
    start_date = end_date - timedelta(days=29)
    
    stats = DailySummaryService.get_period_stats(request.auth, start_date, end_date)
    stats['period'] = 'month'
    
    return stats


@router.post("/water", auth=AuthBearer())
def log_water(request, data: WaterLogSchema):
    log_date = data.date or date.today()
    water_log = WaterService.log_water(request.auth, data.amount_ml, log_date)
    
    return {'success': True, 'total_ml': WaterService.get_daily_water_intake(request.auth, log_date)}


@router.get("/water/today", auth=AuthBearer())
def get_today_water(request):
    total = WaterService.get_daily_water_intake(request.auth, date.today())
    return {'total_ml': total, 'date': date.today()}
