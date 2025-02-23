import asyncio
import logging

from django.conf import settings
from django.core.management.base import BaseCommand

from userbot.generate_session import client

logger = logging.getLogger(__name__)


async def on_start():
    logger.info("Starting user bot")
    await client.start(phone=settings.PHONE_NUMBER, password=settings.PASSWORD)
    logger.info("User bot started")
    await client.run_until_disconnected()


async def on_stop():
    logger.info("Stopping user bot")
    await client.disconnect()
    logger.info("User bot stopped")


class Command(BaseCommand):
    help = "Start telegram user bot"

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            loop.run_until_complete(on_start())
        except KeyboardInterrupt:
            logger.info("KeyboardInterrupt caught. Exiting...")
        finally:
            loop.run_until_complete(on_stop())
            loop.close()
