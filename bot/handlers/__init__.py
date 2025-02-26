from aiogram import Router

from .get_chat_list_handler import get_chat_list_router
from .read_message import read_message_router

handlers_router = Router()

handlers_router.include_routers(get_chat_list_router, read_message_router)
