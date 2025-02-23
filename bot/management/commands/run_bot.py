import asyncio
import logging

from aiogram import Bot
from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils.translation import gettext as _

logger = logging.getLogger(__name__)


async def on_startup(bot: Bot):
    logger.info("Bot is running")

    if settings.BASE_WEBHOOK_URL:
        await bot.set_webhook(f"{settings.BASE_WEBHOOK_URL}{settings.WEBHOOK_PATH}", secret_token=settings.WEBHOOK_SECRET)

    for admin_id in settings.ADMINS:
        await bot.send_message(text=_("Bot is running"), chat_id=admin_id)


async def on_shutdown(bot: Bot):
    logger.info("Bot is turned off")

    await bot.delete_webhook()

    for admin_id in settings.ADMINS:
        await bot.send_message(text=_("Bot is turned off"), chat_id=admin_id)


class Command(BaseCommand):
    help = "Start telegram bot"

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        from bot.generate_session import bot, dp

        dp.startup.register(on_startup)
        dp.shutdown.register(on_shutdown)

        if settings.BASE_WEBHOOK_URL:
            from aiohttp import web
            from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application

            logger.info("Run via webhook")

            app = web.Application()

            webhook_requests_handler = SimpleRequestHandler(
                dispatcher=dp,
                bot=bot,
                secret_token=settings.WEBHOOK_SECRET,
            )
            webhook_requests_handler.register(app, path=settings.WEBHOOK_PATH)

            setup_application(app, dp, bot=bot)

            web.run_app(app, host=settings.WEB_SERVER_HOST, port=settings.WEB_SERVER_PORT)
        else:
            logger.info("Run via polling")
            asyncio.run(dp.start_polling(bot))
