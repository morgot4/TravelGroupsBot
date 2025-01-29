import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.client.bot import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.utils import markdown
from bot.config import settings
from bot import router as bot_v1_router
from bot.database import db_helper
from bot.middlewares import DataBaseSession


async def start_bot(bot: Bot):
    await bot.send_message(
        1008265857, text="*Бот запущен\\!*", parse_mode=ParseMode.MARKDOWN_V2
    )


async def stop_bot(bot: Bot):
    await bot.send_message(
        1008265857, text="*Бот выключен\\!*", parse_mode=ParseMode.MARKDOWN_V2
    )


async def main():
    bot = Bot(
        settings.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN_V2),
    )
    dp = Dispatcher()
    dp.include_router(bot_v1_router)
    dp.startup.register(start_bot)
    dp.shutdown.register(stop_bot)

    dp.update.middleware(DataBaseSession(db_helper.session_factory))
    await bot.delete_webhook(drop_pending_updates=True)

    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
