from aiogram.types import Message
from aiogram.enums import ParseMode
from aiogram.utils import markdown
from sqlalchemy.ext.asyncio import AsyncSession
from bot.database.cruds import orm_select_marks, orm_update_mark, orm_update_mark
from bot.database.models import MarksOrm
from bot.keyboards.builders import get_callback_buttons
from bot.config import bot_manager
from bot.database.cached_cruds import get_cached_mark, get_cached_point, add_cached_mark


async def get_all_marks(message: Message, session: AsyncSession):
    marks = await orm_select_marks(session=session)
    for mark in marks:
        await add_cached_mark(mark=mark)
        await message.answer(
            text=f"Метка: *{markdown.markdown_decoration.quote(mark.mark_code)}*",
            reply_markup=get_callback_buttons(
                buttons={"\U00002b07 Подробнее": f"more_about_mark_{mark.mark_code}"},
                size=(1,),
            ),
            parse_mode=ParseMode.MARKDOWN_V2,
        )


async def clear_mark(mark: MarksOrm, session: AsyncSession):
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


async def clear_all_marks(session: AsyncSession):
    marks = await orm_select_marks(session=session)
    for mark in marks:
        await clear_mark(mark=mark, session=session)


async def check_all_marks(session: AsyncSession):
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


async def get_captain_message(session: AsyncSession, mark_code: str, number: int):
    mark = await get_cached_mark(session=session, key=mark_code, delete=True, find_by="code")
    point = await get_cached_point(session=session, number=number, delete=True)
    if mark.last_point == point.number:
        return None, None
    data = {
        "last_point": point.number
    }
    await orm_update_mark(session=session, mark=mark, data=data)
    await session.close()
    message = point.text
    captain_id = mark.captain_telegram_id

    return captain_id, message
