import jwt
from datetime import datetime, timedelta
from django.conf import settings
from django.contrib.auth import authenticate
from django.core.cache import cache
from typing import Optional, Dict, Any
import structlog
from decimal import Decimal

from .models import User, UserProfile
from .schemas import CalorieCalculationResult

logger = structlog.get_logger(__name__)


class AuthService:
    
    @staticmethod
    def create_tokens(user: User) -> Dict[str, str]:
        access_token = AuthService._create_access_token(user)
        refresh_token = AuthService._create_refresh_token(user)
        
        return {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'token_type': 'bearer'
        }
    
    @staticmethod
    def _create_access_token(user: User) -> str:
        payload = {
            'user_id': user.id,
            'username': user.username,
            'exp': datetime.utcnow() + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES),
            'iat': datetime.utcnow(),
            'type': 'access'
        }
        return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    
    @staticmethod
    def _create_refresh_token(user: User) -> str:
        payload = {
            'user_id': user.id,
            'exp': datetime.utcnow() + timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS),
            'iat': datetime.utcnow(),
            'type': 'refresh'
        }
        return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    
    @staticmethod
    def verify_token(token: str) -> Optional[Dict[str, Any]]:
        try:
            payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("token_expired")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning("invalid_token", error=str(e))
            return None
    
    @staticmethod
    def authenticate_user(username: str, password: str) -> Optional[User]:
        user = authenticate(username=username, password=password)
        if user and user.is_active:
            return user
        return None
    
    @staticmethod
    def authenticate_telegram(telegram_id: int) -> Optional[User]:
        try:
            user = User.objects.get(telegram_id=telegram_id, is_active=True)
            return user
        except User.DoesNotExist:
            return None


class HealthCalculationService:
    
    ACTIVITY_MULTIPLIERS = {
        'sedentary': 1.2,
        'light': 1.375,
        'moderate': 1.55,
        'active': 1.725,
        'very_active': 1.9,
    }
    
    @staticmethod
    def calculate_bmr(profile: UserProfile) -> float:
        weight = float(profile.weight)
        height = float(profile.height)
        age = profile.age or 30  # Default age if not provided
        
        if profile.gender == 'M':
            bmr = 88.362 + (13.397 * weight) + (4.799 * height) - (5.677 * age)
        else:  # Female or Other
            bmr = 447.593 + (9.247 * weight) + (3.098 * height) - (4.330 * age)
        
        return round(bmr, 2)
    
    @staticmethod
    def calculate_tdee(bmr: float, activity_level: str) -> float:
        multiplier = HealthCalculationService.ACTIVITY_MULTIPLIERS.get(activity_level, 1.2)
        tdee = bmr * multiplier
        return round(tdee, 2)
    
    @staticmethod
    def calculate_calorie_target(tdee: float, goal: str) -> int:
        if goal == 'weight_loss':
            target = tdee - 500
        elif goal == 'muscle_gain':
            target = tdee + 300
        else:  # maintenance
            target = tdee
        
        return max(int(target), 1200)  # Minimum 1200 calories
    
    @staticmethod
    def calculate_macros(calorie_target: int, goal: str) -> Dict[str, int]:
        if goal == 'weight_loss':
            protein_ratio = 0.35
            carbs_ratio = 0.35
            fat_ratio = 0.30
        elif goal == 'muscle_gain':
            protein_ratio = 0.30
            carbs_ratio = 0.45
            fat_ratio = 0.25
        else:  # maintenance
            protein_ratio = 0.30
            carbs_ratio = 0.40
            fat_ratio = 0.30
        
        protein_grams = int((calorie_target * protein_ratio) / 4)
        carbs_grams = int((calorie_target * carbs_ratio) / 4)
        fat_grams = int((calorie_target * fat_ratio) / 9)
        
        return {
            'protein': protein_grams,
            'carbs': carbs_grams,
            'fat': fat_grams,
        }
    
    @staticmethod
    def calculate_and_update_profile(profile: UserProfile) -> CalorieCalculationResult:
        bmr = HealthCalculationService.calculate_bmr(profile)
        
        tdee = HealthCalculationService.calculate_tdee(bmr, profile.activity_level)
        
        calorie_target = HealthCalculationService.calculate_calorie_target(tdee, profile.goal)
        
        macros = HealthCalculationService.calculate_macros(calorie_target, profile.goal)
        
        profile.bmr = Decimal(str(bmr))
        profile.tdee = Decimal(str(tdee))
        profile.daily_calorie_target = calorie_target
        profile.daily_protein_target = macros['protein']
        profile.daily_carbs_target = macros['carbs']
        profile.daily_fat_target = macros['fat']
        profile.save()
        
        logger.info(
            "calculated_health_metrics",
            user_id=profile.user.id,
            bmr=bmr,
            tdee=tdee,
            calorie_target=calorie_target,
        )
        
        return CalorieCalculationResult(
            bmr=bmr,
            tdee=tdee,
            daily_calorie_target=calorie_target,
            daily_protein_target=macros['protein'],
            daily_carbs_target=macros['carbs'],
            daily_fat_target=macros['fat'],
        )


class UserCacheService:
    
    CACHE_TTL = 3600  # 1 hour
    
    @staticmethod
    def get_user_cache_key(user_id: int) -> str:
        return f"user:{user_id}"
    
    @staticmethod
    def get_profile_cache_key(user_id: int) -> str:
        return f"user_profile:{user_id}"
    
    @staticmethod
    def cache_user(user: User) -> None:
        cache_key = UserCacheService.get_user_cache_key(user.id)
        cache.set(cache_key, user, UserCacheService.CACHE_TTL)
    
    @staticmethod
    def get_cached_user(user_id: int) -> Optional[User]:
        cache_key = UserCacheService.get_user_cache_key(user_id)
        return cache.get(cache_key)
    
    @staticmethod
    def invalidate_user_cache(user_id: int) -> None:
        user_key = UserCacheService.get_user_cache_key(user_id)
        profile_key = UserCacheService.get_profile_cache_key(user_id)
        cache.delete_many([user_key, profile_key])
