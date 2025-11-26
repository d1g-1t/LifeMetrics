from ninja.security import HttpBearer
from django.contrib.auth.models import AnonymousUser
from typing import Optional
import structlog

from apps.users.services import AuthService
from apps.users.models import User

logger = structlog.get_logger(__name__)


class AuthBearer(HttpBearer):
    
    def authenticate(self, request, token: str) -> Optional[User]:
        payload = AuthService.verify_token(token)
        
        if not payload:
            return None
        
        user_id = payload.get('user_id')
        if not user_id:
            return None
        
        try:
            user = User.objects.get(id=user_id, is_active=True)
            return user
        except User.DoesNotExist:
            logger.warning("user_not_found", user_id=user_id)
            return None
