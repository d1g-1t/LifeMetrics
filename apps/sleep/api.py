from ninja import Router
from typing import List
from datetime import date, time
from decimal import Decimal
from apps.core.auth import AuthBearer
from .models import SleepLog
from pydantic import BaseModel, Field


router = Router()


class SleepLogCreateSchema(BaseModel):
    date: date
    bedtime: time
    wake_time: time
    duration_hours: Decimal = Field(..., gt=0)
    quality: int = Field(..., ge=1, le=5)
    notes: str = ""


class SleepLogSchema(BaseModel):
    id: int
    date: date
    bedtime: time
    wake_time: time
    duration_hours: Decimal
    quality: int
    notes: str
    
    class Config:
        from_attributes = True


@router.post("/log", response=SleepLogSchema, auth=AuthBearer())
def log_sleep(request, data: SleepLogCreateSchema):
    sleep_log, created = SleepLog.objects.update_or_create(
        user=request.auth,
        date=data.date,
        defaults={
            'bedtime': data.bedtime,
            'wake_time': data.wake_time,
            'duration_hours': data.duration_hours,
            'quality': data.quality,
            'notes': data.notes,
        }
    )
    return sleep_log


@router.get("/logs", response=List[SleepLogSchema], auth=AuthBearer())
def get_sleep_logs(request, days: int = 7):
    logs = SleepLog.objects.filter(user=request.auth)[:days]
    return list(logs)
