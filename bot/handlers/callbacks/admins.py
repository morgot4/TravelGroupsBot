from aiogram import Router, F
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession
from bot.database.cached_cruds import (
    get_cached_admin,
)
from bot.database.cruds import orm_delete_admin
from bot.keyboards import rmk

router = Router()

@router.callback_query(F.data.startswith("delete_admin_"))
async def delete_admin(callback: CallbackQuery, session: AsyncSession):
    telegram_id = "_".join(callback.data.split("_")[2:])
    admin = await get_cached_admin(
        session=session, admin_telegram_id=str(telegram_id), delete=True
    )
    if admin is not None:
        await callback.message.delete()
        await orm_delete_admin(session=session, telegram_id=admin.telegram_id)
    else:
        await callback.message.answer(
            "Администратора уже не существует, обновите список", reply_markup=rmk
        )
    await callback.answer()