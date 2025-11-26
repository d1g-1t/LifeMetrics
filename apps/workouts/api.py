from ninja import Router
from typing import List
from datetime import date
from apps.core.auth import AuthBearer
from .models import Workout, WorkoutLog
from pydantic import BaseModel, Field
from decimal import Decimal


router = Router()


class WorkoutSchema(BaseModel):
    id: int
    name: str
    category: str
    calories_per_hour: int
    
    class Config:
        from_attributes = True


class WorkoutLogCreateSchema(BaseModel):
    workout_id: int
    date: date
    duration_minutes: int = Field(..., gt=0)
    calories_burned: int = Field(..., ge=0)
    distance_km: Decimal | None = None
    notes: str = ""


class WorkoutLogSchema(BaseModel):
    id: int
    workout: WorkoutSchema
    date: date
    duration_minutes: int
    calories_burned: int
    distance_km: Decimal | None
    
    class Config:
        from_attributes = True


@router.get("/list", response=List[WorkoutSchema], auth=AuthBearer())
def list_workouts(request):
    workouts = Workout.objects.filter(is_public=True)
    return list(workouts)


@router.post("/log", response=WorkoutLogSchema, auth=AuthBearer())
def log_workout(request, data: WorkoutLogCreateSchema):
    workout_log = WorkoutLog.objects.create(
        user=request.auth,
        workout_id=data.workout_id,
        date=data.date,
        duration_minutes=data.duration_minutes,
        calories_burned=data.calories_burned,
        distance_km=data.distance_km,
        notes=data.notes,
    )
    return workout_log


@router.get("/logs", response=List[WorkoutLogSchema], auth=AuthBearer())
def get_workout_logs(request, date: date = None):
    logs = WorkoutLog.objects.filter(user=request.auth).select_related('workout')
    if date:
        logs = logs.filter(date=date)
    return list(logs[:30])
