from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from ninja import NinjaAPI
from apps.core.api import router as core_router
from apps.users.api import router as users_router
from apps.food.api import router as food_router
from apps.workouts.api import router as workouts_router
from apps.sleep.api import router as sleep_router
from apps.goals.api import router as goals_router
from apps.telegram_bot.api import router as telegram_router

api = NinjaAPI(
    title="LifeMetrics API",
    version="1.0.0",
    description="Comprehensive Health & Fitness Tracking Platform",
    docs_url="/api/docs",
)

api.add_router("/", core_router, tags=["Core"])
api.add_router("/auth", users_router, tags=["Authentication"])
api.add_router("/food", food_router, tags=["Food & Nutrition"])
api.add_router("/workouts", workouts_router, tags=["Workouts"])
api.add_router("/sleep", sleep_router, tags=["Sleep"])
api.add_router("/goals", goals_router, tags=["Goals"])
api.add_router("/telegram", telegram_router, tags=["Telegram"])

urlpatterns = [
    path('admin/', admin.site.admin),
    path('api/', api.urls),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    
    if 'debug_toolbar' in settings.INSTALLED_APPS:
        import debug_toolbar
        urlpatterns = [path('__debug__/', include(debug_toolbar.urls))] + urlpatterns
