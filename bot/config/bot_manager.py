from aiogram import Bot, Dispatcher, F
from aiogram.client.bot import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.redis import RedisStorage
from .settings import settings
from bot.database.redis_helper import redis_helper
from aioredis import Redis


class BotManager:
    def __init__(self, token: str, redis: Redis):
        self.bot = Bot(
            token=token, default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN_V2)
        )
        self.dp = Dispatcher(bot=self.bot, storage=RedisStorage(redis=redis))

    def get_bot(self):
        return self.bot

    def get_dispatcher(self):
        return self.dp


bot_manager = BotManager(token=settings.BOT_TOKEN, redis=redis_helper.redis)
