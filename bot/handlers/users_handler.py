from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

router = Router()
@router.message(Command("start"))
async def start(message: Message):
    await message.answer(f"Привет, вот твой ID: {message.from_user.id}")