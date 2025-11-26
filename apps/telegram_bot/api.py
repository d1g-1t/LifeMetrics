from ninja import Router
from django.http import HttpResponse
import structlog

router = Router()
logger = structlog.get_logger(__name__)


@router.post("/webhook", auth=None)
async def telegram_webhook(request):
    return HttpResponse("OK")


@router.get("/set-webhook", auth=None)
async def set_webhook(request):
    from django.conf import settings
    from .bot import bot
    
    webhook_url = settings.TELEGRAM_WEBHOOK_URL
    if webhook_url:
        await bot.set_webhook(
            url=webhook_url,
            secret_token=settings.TELEGRAM_WEBHOOK_SECRET
        )
        return {"status": "webhook_set", "url": webhook_url}
    
    return {"status": "no_webhook_url"}


@router.get("/delete-webhook", auth=None)
async def delete_webhook(request):
    from .bot import bot
    
    await bot.delete_webhook()
    return {"status": "webhook_deleted"}
