import json

import redis.asyncio as aioredis
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from django.conf import settings
from aiogram.enums import ParseMode

get_chat_list_router = Router()

redis = aioredis.from_url(
    f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/{settings.REDIS_PUBSUB_DB}",
    decode_responses=True
)


@get_chat_list_router.message(Command("get_chat_list"))
async def get_chat_list(message: Message):
    pubsub = redis.pubsub()
    await pubsub.subscribe(settings.REDIS_PUBSUB_CHANNEL + "_response")

    await redis.publish(settings.REDIS_PUBSUB_CHANNEL, "get_chat_list")

    async for pubsub_message in pubsub.listen():
        # message — это dict вида:
        # {
        #    "type": "message",
        #    "pattern": None,
        #    "channel": "channel_name",
        #    "data": "..."
        # }
        if pubsub_message["type"] == "message":
            raw_data = pubsub_message["data"]
            chats = json.loads(raw_data)["chat_list"]
            for i in range(0, len(chats), 50):
                batch = chats[i: i + 50]
                await message.answer("\n".join(batch), parse_mode=ParseMode.MARKDOWN)
            await pubsub.unsubscribe()
            break
