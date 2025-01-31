from telethon import TelegramClient
from telethon.tl.functions.users import GetFullUserRequest
from telethon.types import UserFull
from bot.config import settings


async def get_user(username: str) -> UserFull:
    async with TelegramClient("gesu1337", settings.API_ID, settings.API_HASH) as client:
        try:
            user = await client(GetFullUserRequest(username))
        except Exception as exp:
            print(exp)
            return None
    return user


