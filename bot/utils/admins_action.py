from aiogram.types import Message
from aiogram.enums import ParseMode
from aiogram.utils import markdown
from sqlalchemy.ext.asyncio import AsyncSession
from bot.database.cruds import orm_select_admins
from bot.keyboards.builders import get_callback_buttons
from bot.config import bot_manager


async def get_all_admins(message: Message, session: AsyncSession):
    admins = await orm_select_admins(session=session)
    for admin in admins:
        await message.answer(
            text=f"Администратор: @{markdown.markdown_decoration.quote(admin.username)}",
            reply_markup=get_callback_buttons(
                buttons={"\U0001f5d1 Удалить": f"delete_admin_{admin.telegram_id}"},
                size=(1,),
            ),
            parse_mode=ParseMode.MARKDOWN_V2,
        )
