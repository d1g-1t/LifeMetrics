from pydantic import BaseModel, Field, EmailStr, validator
from typing import Optional
from datetime import date, datetime
from decimal import Decimal


class UserProfileSchema(BaseModel):
    gender: str = Field(..., pattern='^[MFO]$')
    date_of_birth: Optional[date] = None
    height: Decimal = Field(..., gt=0, le=300, description="Height in cm")
    weight: Decimal = Field(..., gt=0, le=500, description="Weight in kg")
    activity_level: str = Field(..., pattern='^(sedentary|light|moderate|active|very_active)$')
    goal: str = Field(..., pattern='^(weight_loss|maintenance|muscle_gain)$')
    target_weight: Optional[Decimal] = Field(None, gt=0, le=500)
    timezone: str = Field(default='Europe/Moscow')
    language: str = Field(default='ru')
    notifications_enabled: bool = Field(default=True)
    
    class Config:
        from_attributes = True


class UserProfileUpdateSchema(BaseModel):
    gender: Optional[str] = Field(None, pattern='^[MFO]$')
    date_of_birth: Optional[date] = None
    height: Optional[Decimal] = Field(None, gt=0, le=300)
    weight: Optional[Decimal] = Field(None, gt=0, le=500)
    activity_level: Optional[str] = Field(None, pattern='^(sedentary|light|moderate|active|very_active)$')
    goal: Optional[str] = Field(None, pattern='^(weight_loss|maintenance|muscle_gain)$')
    target_weight: Optional[Decimal] = Field(None, gt=0, le=500)
    timezone: Optional[str] = None
    language: Optional[str] = None
    notifications_enabled: Optional[bool] = None
    
    class Config:
        from_attributes = True


class UserRegistrationSchema(BaseModel):
    username: str = Field(..., min_length=3, max_length=150)
    email: Optional[EmailStr] = None
    password: str = Field(..., min_length=8)
    telegram_id: Optional[int] = None
    telegram_username: Optional[str] = None
    
    class Config:
        from_attributes = True


class UserLoginSchema(BaseModel):
    username: str
    password: str


class TelegramAuthSchema(BaseModel):
    telegram_id: int
    telegram_username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class TokenSchema(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class UserResponseSchema(BaseModel):
    id: int
    username: str
    email: Optional[str] = None
    telegram_id: Optional[int] = None
    telegram_username: Optional[str] = None
    is_premium: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class CalorieCalculationResult(BaseModel):
    bmr: float = Field(..., description="Basal Metabolic Rate")
    tdee: float = Field(..., description="Total Daily Energy Expenditure")
    daily_calorie_target: int
    daily_protein_target: int = Field(..., description="in grams")
    daily_carbs_target: int = Field(..., description="in grams")
    daily_fat_target: int = Field(..., description="in grams")
    
    class Config:
        from_attributes = True
