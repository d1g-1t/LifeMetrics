from django.core.management.base import BaseCommand
import asyncio
import structlog

from apps.telegram_bot.bot import bot, dp
from apps.telegram_bot.handlers import router

logger = structlog.get_logger(__name__)


class Command(BaseCommand):
    help = 'Run Telegram bot in polling mode'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting Telegram bot...'))
        
        dp.include_router(router)
        
        asyncio.run(self.start_bot())

    async def start_bot(self):
        try:
            await bot.delete_webhook(drop_pending_updates=True)
            
            logger.info("telegram_bot_started")
            self.stdout.write(self.style.SUCCESS('Bot is running...'))
            
            await dp.start_polling(bot)
        except Exception as e:
            logger.error("bot_startup_failed", error=str(e))
            self.stdout.write(self.style.ERROR(f'Failed to start bot: {e}'))
