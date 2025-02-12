from aiogram import Bot, Dispatcher, F
from aiogram.client.bot import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.redis import RedisStorage
from .settings import settings
from telethon import TelegramClient


class BotManager:
    def __init__(self, token: str):
        self.bot = Bot(
            token=token, default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN_V2)
        )
        self.client = TelegramClient(
            settings.API_USERNAME, settings.API_ID, settings.API_HASH
        )
        self.dp = Dispatcher(bot=self.bot)

    def get_bot(self):
        return self.bot

    def get_dispatcher(self):
        return self.dp

    def get_client(self):
        return self.client


bot_manager = BotManager(
    token=settings.BOT_TOKEN,
)
