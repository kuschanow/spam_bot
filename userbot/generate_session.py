from django.conf import settings
from telethon import TelegramClient

client = TelegramClient(settings.SESSION_PATH, settings.API_ID, settings.API_HASH)
