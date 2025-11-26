import time
import structlog
from django.core.cache import cache
from django.http import JsonResponse
from django.conf import settings

logger = structlog.get_logger(__name__)


class RequestLoggingMiddleware:
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start_time = time.time()
        
        logger.info(
            "request_started",
            method=request.method,
            path=request.path,
            ip=self.get_client_ip(request),
        )
        
        response = self.get_response(request)
        
        duration = time.time() - start_time
        logger.info(
            "request_finished",
            method=request.method,
            path=request.path,
            status=response.status_code,
            duration=f"{duration:.3f}s",
        )
        
        return response

    @staticmethod
    def get_client_ip(request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class RateLimitMiddleware:
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not self.check_rate_limit(request):
            return JsonResponse(
                {'error': 'Rate limit exceeded. Please try again later.'},
                status=429
            )
        
        return self.get_response(request)

    def check_rate_limit(self, request):
        if request.path.startswith('/static/') or request.path.startswith('/admin/'):
            return True
        
        ip = self.get_client_ip(request)
        minute_key = f"rate_limit:minute:{ip}"
        hour_key = f"rate_limit:hour:{ip}"
        
        minute_count = cache.get(minute_key, 0)
        if minute_count >= settings.RATE_LIMIT_PER_MINUTE:
            logger.warning("rate_limit_exceeded", ip=ip, window="minute")
            return False
        
        hour_count = cache.get(hour_key, 0)
        if hour_count >= settings.RATE_LIMIT_PER_HOUR:
            logger.warning("rate_limit_exceeded", ip=ip, window="hour")
            return False
        
        cache.set(minute_key, minute_count + 1, 60)
        cache.set(hour_key, hour_count + 1, 3600)
        
        return True

    @staticmethod
    def get_client_ip(request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
