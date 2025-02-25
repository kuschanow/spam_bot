import redis.asyncio as aioredis
from aiogram import Router, F
from aiogram.filters import Command, MagicData
from aiogram.types import Message
from django.conf import settings

get_chat_list_router = Router()

redis = aioredis.from_url(
    f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/{settings.REDIS_PUBSUB_DB}",
    decode_responses=True
)


@get_chat_list_router.message(Command("get_chat_list"), MagicData(F.message.chat.id._is(2044164706)))
async def get_chat_list(message: Message):
    pubsub = redis.pubsub()
    await pubsub.subscribe(settings.REDIS_PUBSUB_CHANNEL)

    redis.publish(settings.REDIS_PUBSUB_CHANNEL, {"message": "get_chat_list"})

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
            await message.answer(raw_data)
