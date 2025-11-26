from ninja import Router
from django.shortcuts import get_object_or_404
from django.contrib.auth.hashers import make_password
from typing import List
import structlog

from .models import User, UserProfile
from .schemas import (
    UserRegistrationSchema,
    UserLoginSchema,
    TelegramAuthSchema,
    TokenSchema,
    UserResponseSchema,
    UserProfileSchema,
    UserProfileUpdateSchema,
    CalorieCalculationResult,
)
from .services import AuthService, HealthCalculationService, UserCacheService
from apps.core.auth import AuthBearer

router = Router()
logger = structlog.get_logger(__name__)


@router.post("/register", response=UserResponseSchema)
def register(request, data: UserRegistrationSchema):
    if User.objects.filter(username=data.username).exists():
        return router.create_response(
            request,
            {'error': 'Username already exists'},
            status=400
        )
    
    user = User.objects.create(
        username=data.username,
        email=data.email,
        password=make_password(data.password),
        telegram_id=data.telegram_id,
        telegram_username=data.telegram_username,
    )
    
    logger.info("user_registered", user_id=user.id, username=user.username)
    
    return user


@router.post("/login", response=TokenSchema)
def login(request, data: UserLoginSchema):
    user = AuthService.authenticate_user(data.username, data.password)
    
    if not user:
        return router.create_response(
            request,
            {'error': 'Invalid credentials'},
            status=401
        )
    
    tokens = AuthService.create_tokens(user)
    
    logger.info("user_logged_in", user_id=user.id)
    
    return tokens


@router.post("/telegram-auth", response=TokenSchema)
def telegram_auth(request, data: TelegramAuthSchema):
    user = AuthService.authenticate_telegram(data.telegram_id)
    
    if not user:
        username = data.telegram_username or f"tg_{data.telegram_id}"
        user = User.objects.create(
            username=username,
            telegram_id=data.telegram_id,
            telegram_username=data.telegram_username,
            telegram_first_name=data.first_name,
            telegram_last_name=data.last_name,
        )
        logger.info("telegram_user_registered", user_id=user.id, telegram_id=data.telegram_id)
    
    tokens = AuthService.create_tokens(user)
    
    logger.info("telegram_user_authenticated", user_id=user.id, telegram_id=data.telegram_id)
    
    return tokens


@router.get("/me", response=UserResponseSchema, auth=AuthBearer())
def get_current_user(request):
    return request.auth


@router.get("/profile", response=UserProfileSchema, auth=AuthBearer())
def get_profile(request):
    profile = get_object_or_404(UserProfile, user=request.auth)
    return profile


@router.post("/profile", response=UserProfileSchema, auth=AuthBearer())
def create_profile(request, data: UserProfileSchema):
    if UserProfile.objects.filter(user=request.auth).exists():
        return router.create_response(
            request,
            {'error': 'Profile already exists'},
            status=400
        )
    
    profile = UserProfile.objects.create(
        user=request.auth,
        **data.dict()
    )
    
    HealthCalculationService.calculate_and_update_profile(profile)
    
    logger.info("profile_created", user_id=request.auth.id)
    
    return profile


@router.put("/profile", response=UserProfileSchema, auth=AuthBearer())
def update_profile(request, data: UserProfileUpdateSchema):
    profile = get_object_or_404(UserProfile, user=request.auth)
    
    for field, value in data.dict(exclude_unset=True).items():
        setattr(profile, field, value)
    
    profile.save()
    
    HealthCalculationService.calculate_and_update_profile(profile)
    
    UserCacheService.invalidate_user_cache(request.auth.id)
    
    logger.info("profile_updated", user_id=request.auth.id)
    
    return profile


@router.get("/profile/calculate-calories", response=CalorieCalculationResult, auth=AuthBearer())
def calculate_calories(request):
    profile = get_object_or_404(UserProfile, user=request.auth)
    
    result = HealthCalculationService.calculate_and_update_profile(profile)
    
    return result
