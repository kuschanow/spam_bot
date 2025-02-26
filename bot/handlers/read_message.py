from aiogram import Router, F
from aiogram.enums import ParseMode
from aiogram.types import Message

read_message_router = Router()


@read_message_router.message(F.text)
async def read_message(message: Message):
    await message.answer(f'```\n{message.html_text}\n```', parse_mode=ParseMode.MARKDOWN_V2)
