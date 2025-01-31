from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton


def get_confirmation_menu():
    keyboard_builder = InlineKeyboardBuilder()
    keyboard_builder.add(
        InlineKeyboardButton(text=f"\U00002705 Да", callback_data="yes_clear")
    )
    keyboard_builder.add(
        InlineKeyboardButton(text=f"\U0000274c Нет", callback_data="no_clear")
    )
    keyboard_builder.adjust(1, 1)
    return keyboard_builder.as_markup()
