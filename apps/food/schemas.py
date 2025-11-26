from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import date, datetime
from decimal import Decimal


class FoodSchema(BaseModel):
    id: Optional[int] = None
    name: str = Field(..., min_length=1, max_length=255)
    brand: Optional[str] = Field(None, max_length=255)
    calories: Decimal = Field(..., ge=0)
    protein: Decimal = Field(..., ge=0)
    carbs: Decimal = Field(..., ge=0)
    fat: Decimal = Field(..., ge=0)
    fiber: Decimal = Field(default=0, ge=0)
    sugar: Decimal = Field(default=0, ge=0)
    serving_size: Decimal = Field(default=100, ge=0)
    barcode: Optional[str] = Field(None, max_length=50)
    is_verified: bool = False
    
    class Config:
        from_attributes = True


class FoodCreateSchema(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    brand: Optional[str] = Field(None, max_length=255)
    calories: Decimal = Field(..., ge=0)
    protein: Decimal = Field(..., ge=0)
    carbs: Decimal = Field(..., ge=0)
    fat: Decimal = Field(..., ge=0)
    fiber: Decimal = Field(default=0, ge=0)
    sugar: Decimal = Field(default=0, ge=0)
    serving_size: Decimal = Field(default=100, ge=0)
    barcode: Optional[str] = None


class FoodLogSchema(BaseModel):
    id: Optional[int] = None
    food_id: int
    food_name: Optional[str] = None
    date: date
    meal_type: str = Field(..., pattern='^(breakfast|lunch|dinner|snack)$')
    serving_amount: Decimal = Field(..., gt=0)
    calories: Optional[Decimal] = None
    protein: Optional[Decimal] = None
    carbs: Optional[Decimal] = None
    fat: Optional[Decimal] = None
    notes: Optional[str] = None
    
    class Config:
        from_attributes = True


class FoodLogCreateSchema(BaseModel):
    food_id: int
    date: date
    meal_type: str = Field(..., pattern='^(breakfast|lunch|dinner|snack)$')
    serving_amount: Decimal = Field(..., gt=0)
    notes: Optional[str] = None


class DailySummarySchema(BaseModel):
    date: date
    total_calories: Decimal
    total_protein: Decimal
    total_carbs: Decimal
    total_fat: Decimal
    target_calories: Optional[int] = None
    target_protein: Optional[int] = None
    target_carbs: Optional[int] = None
    target_fat: Optional[int] = None
    breakfast_calories: Decimal
    lunch_calories: Decimal
    dinner_calories: Decimal
    snack_calories: Decimal
    water_intake_ml: int
    weight: Optional[Decimal] = None
    calorie_percentage: Optional[float] = None
    
    class Config:
        from_attributes = True


class WaterLogSchema(BaseModel):
    amount_ml: int = Field(..., gt=0)
    date: Optional[date] = None


class FoodSearchResultSchema(BaseModel):
    foods: List[FoodSchema]
    total: int


class MacroBreakdownSchema(BaseModel):
    protein: Decimal
    carbs: Decimal
    fat: Decimal
    protein_percentage: float
    carbs_percentage: float
    fat_percentage: float


class NutritionStatsSchema(BaseModel):
    period: str  # 'week', 'month'
    avg_calories: float
    avg_protein: float
    avg_carbs: float
    avg_fat: float
    days_logged: int
    total_days: int
    adherence_percentage: float
