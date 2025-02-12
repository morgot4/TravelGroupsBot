from aiogram.utils.keyboard import (
    ReplyKeyboardBuilder,
    InlineKeyboardBuilder,
    InlineKeyboardButton,
)


def profile(text: str | list):
    builder = ReplyKeyboardBuilder()

    if isinstance(text, str):
        text = [text]

    [builder.button(text=txt) for txt in text]
    builder.adjust(*[1] * len(text))
    return builder.as_markup(resize_keyboard=True, one_time_keyboard=False)


def get_callback_buttons(*, buttons: dict[str, str], size: tuple[int] = (2,)):
    keyboard = InlineKeyboardBuilder()

    for text, data in buttons.items():
        keyboard.add(InlineKeyboardButton(text=text, callback_data=data))
    return keyboard.adjust(*size).as_markup()
