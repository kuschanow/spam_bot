import asyncio
import json
import logging

import redis.asyncio as aioredis
from django.conf import settings
from django.core.management.base import BaseCommand

from userbot.generate_session import client

logger = logging.getLogger(__name__)


async def handle_messages():
    redis_conn = aioredis.from_url(
        f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/{settings.REDIS_PUBSUB_DB}",
        decode_responses=True
    )
    pubsub = redis_conn.pubsub()
    await pubsub.subscribe(settings.REDIS_PUBSUB_CHANNEL)

    try:
        async for message in pubsub.listen():
            if message["type"] == "message":
                raw_data = message["data"]
                if raw_data == "get_chat_list":
                    dialogs = await client.get_dialogs()
                    await redis_conn.publish(
                        settings.REDIS_PUBSUB_CHANNEL + "_response",
                        json.dumps({"chat_list": [f"{d.name}, `{d.entity.id}`" for d in dialogs]})
                    )
    except asyncio.CancelledError:
        # Очищаемся, если таск отменят
        logger.info("handle_messages() cancelled")
    finally:
        # Закрываем pubsub
        await pubsub.unsubscribe(settings.REDIS_PUBSUB_CHANNEL)
        await pubsub.close()


async def main():
    logger.info("Starting user bot")
    await client.start(phone=settings.PHONE_NUMBER, password=settings.PASSWORD)
    logger.info("User bot started")

    # Запускаем 2 параллельные задачи:
    #  1. Сам Telethon-клиент (до disconnect)
    #  2. Чтение сообщений из Redis PubSub
    task = asyncio.create_task(handle_messages())
    try:
        await client.run_until_disconnected()
    except KeyboardInterrupt:
        logger.info("KeyboardInterrupt caught")
    finally:
        # Останавливаем client, отменяем нашу таску
        logger.info("Stopping user bot")
        await client.disconnect()
        task.cancel()
        await asyncio.gather(task, return_exceptions=True)
        logger.info("User bot stopped")


class Command(BaseCommand):
    help = "Start telegram user bot"

    def handle(self, *args, **options):
        asyncio.run(main())
