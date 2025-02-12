from aiogram.types import Message
from aiogram.enums import ParseMode
from aiogram.utils import markdown
from sqlalchemy.ext.asyncio import AsyncSession
from bot.database.cruds import orm_select_points
from bot.database.models import MarksOrm
from bot.database.cached_cruds import add_cached_point
from bot.keyboards.builders import get_callback_buttons
from bot.keyboards import admin_mark_keyboard
from bot.config import bot_manager


async def get_all_points(message: Message, session: AsyncSession):
    points = await orm_select_points(session=session)
    points = sorted(points, key=lambda x: x.number)
    for point in points:
        await add_cached_point(point=point)
        await message.answer(
            text=f"Точка *\\#{markdown.markdown_decoration.quote(str(point.number))}*",
            reply_markup=get_callback_buttons(
                buttons={"\U00002b07 Подробнее": f"more_about_point_{point.number}"},
                size=(1,),
            ),
            parse_mode=ParseMode.MARKDOWN_V2,
        )
