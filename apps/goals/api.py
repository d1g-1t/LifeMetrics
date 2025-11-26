from ninja import Router
from typing import List
from datetime import date
from decimal import Decimal
from apps.core.auth import AuthBearer
from .models import Goal, Achievement, UserAchievement
from pydantic import BaseModel, Field


router = Router()


class GoalCreateSchema(BaseModel):
    goal_type: str
    title: str
    description: str = ""
    target_value: Decimal
    start_date: date
    target_date: date


class GoalSchema(BaseModel):
    id: int
    goal_type: str
    title: str
    description: str
    target_value: Decimal
    current_value: Decimal
    start_date: date
    target_date: date
    status: str
    progress_percentage: float
    
    class Config:
        from_attributes = True


class AchievementSchema(BaseModel):
    id: int
    name: str
    description: str
    category: str
    points: int
    
    class Config:
        from_attributes = True


@router.post("/create", response=GoalSchema, auth=AuthBearer())
def create_goal(request, data: GoalCreateSchema):
    goal = Goal.objects.create(
        user=request.auth,
        **data.dict()
    )
    return goal


@router.get("/list", response=List[GoalSchema], auth=AuthBearer())
def list_goals(request, status: str = "active"):
    goals = Goal.objects.filter(user=request.auth, status=status)
    return list(goals)


@router.get("/achievements", response=List[AchievementSchema], auth=AuthBearer())
def get_achievements(request):
    user_achievements = UserAchievement.objects.filter(user=request.auth).select_related('achievement')
    achievements = [ua.achievement for ua in user_achievements]
    return achievements
