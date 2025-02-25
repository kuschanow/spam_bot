from aiogram import Router

from .get_chat_list_handler import get_chat_list_router

handlers_router = Router()

handlers_router.include_router(get_chat_list_router)
