from ninja import Router
from django.http import JsonResponse
from django.db import connection
from django.core.cache import cache
import structlog

router = Router()
logger = structlog.get_logger(__name__)


@router.get("/health", auth=None)
def health_check(request):
    checks = {
        'status': 'healthy',
        'database': check_database(),
        'cache': check_cache(),
    }
    
    all_healthy = all(v == 'ok' for k, v in checks.items() if k != 'status')
    checks['status'] = 'healthy' if all_healthy else 'unhealthy'
    
    status_code = 200 if all_healthy else 503
    
    return JsonResponse(checks, status=status_code)


def check_database():
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        return 'ok'
    except Exception as e:
        logger.error("database_check_failed", error=str(e))
        return 'error'


def check_cache():
    try:
        cache.set('health_check', 'ok', 10)
        result = cache.get('health_check')
        return 'ok' if result == 'ok' else 'error'
    except Exception as e:
        logger.error("cache_check_failed", error=str(e))
        return 'error'


@router.get("/version", auth=None)
def version(request):
    return {
        'version': '1.0.0',
        'api': 'LifeMetrics',
        'environment': 'production',
    }
