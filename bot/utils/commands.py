from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeDefault


async def set_commands(bot: Bot):
    commands = [BotCommand(command="start", description="Старт"), BotCommand(command="labels", description="Мои метки"), BotCommand(command="history", description="История маршрута")]
    await bot.set_my_commands(commands, BotCommandScopeDefault())
