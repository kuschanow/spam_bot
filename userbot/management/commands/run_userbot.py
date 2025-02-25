import asyncio
import logging

import redis.asyncio as aioredis
from django.conf import settings
from django.core.management.base import BaseCommand

from userbot.generate_session import client

logger = logging.getLogger(__name__)


async def handle_messages():
    redis = aioredis.from_url(
        f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/{settings.REDIS_PUBSUB_DB}",
        decode_responses=True
    )
    pubsub = redis.pubsub()
    await pubsub.subscribe(settings.REDIS_PUBSUB_CHANNEL)

    async for message in pubsub.listen():
        # message — это dict вида:
        # {
        #    "type": "message",
        #    "pattern": None,
        #    "channel": "channel_name",
        #    "data": "..."
        # }
        if message["type"] == "message":
            raw_data = message["data"]
            if raw_data.get("message") == "get_chat_list":
                dialogs = await client.get_dialogs()
                redis.publish(settings.REDIS_PUBSUB_CHANNEL, {"chat_list": [f"{dialog.name}, {dialog.entity.id}" for dialog in dialogs]})


async def on_start():
    logger.info("Starting user bot")
    await client.start(phone=settings.PHONE_NUMBER, password=settings.PASSWORD)
    logger.info("User bot started")
    asyncio.create_task(handle_messages())
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
