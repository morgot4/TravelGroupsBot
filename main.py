import asyncio
from aiogram import Bot
from aiogram.enums import ParseMode
from bot.config import bot_manager
from bot import router as bot_v1_router
from bot.database import db_helper
from bot.middlewares import DataBaseSession
from bot.utils.marks_actions import get_captain_message
from bot.utils.commands import set_commands
from bot.config import settings


async def start_bot(bot: Bot):
    await set_commands(bot)
    await bot.send_message(
        1008265857, text="*Бот запущен\\!*", parse_mode=ParseMode.MARKDOWN_V2
    )


async def stop_bot(bot: Bot):
    await bot.send_message(
        1008265857, text="*Бот выключен\\!*", parse_mode=ParseMode.MARKDOWN_V2
    )


client = bot_manager.get_client()


async def main():
    dp = bot_manager.get_dispatcher()
    bot = bot_manager.get_bot()
    dp.include_router(bot_v1_router)
    dp.update.middleware(DataBaseSession(db_helper.session_factory))
    dp.startup.register(start_bot)
    dp.shutdown.register(stop_bot)
    await bot.delete_webhook(drop_pending_updates=True)

    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


with client:
    client.loop.run_until_complete(main())
