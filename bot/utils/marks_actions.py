from aiogram.types import Message
from aiogram.enums import ParseMode
from aiogram.utils import markdown
from sqlalchemy.ext.asyncio import AsyncSession
from bot.database.cruds import orm_select_marks, orm_select_mark, orm_update_mark
from bot.keyboards.builders import get_callback_buttons
from bot.keyboards import admin_mark_keyboard
from bot.config import bot_manager


async def get_all_marks(message: Message, session: AsyncSession):
    marks = await orm_select_marks(session=session)
    for mark in marks:
        await message.answer(
            text=f"Метка: *{markdown.markdown_decoration.quote(mark.mark_code)}*",
            reply_markup=get_callback_buttons(
                buttons={"\U00002b07 Подробнее": f"more_about_mark_{mark.mark_code}"},
                size=(1,),
            ),
            parse_mode=ParseMode.MARKDOWN_V2,
        )


async def clear_all_marks(message: Message, session: AsyncSession):
    marks = await orm_select_marks(session=session)
    for mark in marks:
        id = mark.captain_telegram_id
        if id is not None:
            await bot_manager.get_bot().send_message(
                chat_id=id, text="Вы больше не привязаны к меткам"
            )
        await orm_update_mark(
            session=session,
            mark=mark,
            data={
                "mark_code": f"{mark.mark_code}",
                "captain_username": None,
                "captain_telegram_id": None,
                "captain_phone_number": None,
            },
        )


async def check_all_marks(message: Message, session: AsyncSession):
    marks = await orm_select_marks(session=session)
    bad_marks = []
    for mark in marks:
        telegram_id = mark.captain_telegram_id
        if telegram_id is not None:
            await bot_manager.get_bot().send_message(
                chat_id=telegram_id,
                text=f"Проверка меток\\. Код вашей метки\\: *{markdown.markdown_decoration.quote(mark.mark_code)}*",
                parse_mode=ParseMode.MARKDOWN_V2,
            )
        else:
            bad_marks.append(mark.mark_code)
    return bad_marks
