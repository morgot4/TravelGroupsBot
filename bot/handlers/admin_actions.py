from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.utils import markdown
from aiogram.enums import ParseMode
from bot.utils.states import AdminActions
from sqlalchemy.ext.asyncio import AsyncSession
from bot.keyboards import admin_admins_keyboard, profile
from bot.keyboards.builders import get_callback_buttons
from bot.database.cruds import orm_add_admin, orm_select_admin
from bot.utils import get_user

router = Router()


@router.message(AdminActions.add_admin, F.text == "\U0001f519 Назад")
async def back_admin_menu(message: Message, state: FSMContext):
    await message.answer(
        text=markdown.markdown_decoration.quote("Добавление администратора отмененно"),
        reply_markup=admin_admins_keyboard,
    )
    await state.clear()


@router.message(AdminActions.add_admin, F.text)
async def add_admin(message: Message, state: FSMContext, session: AsyncSession):
    data = await state.get_data()
    admin = await get_user(message.text)
    if admin is not None:
        telegram_id = admin.full_user.id
        if await orm_select_admin(session=session, telegram_id=telegram_id) is not None:
            await message.answer(
                text=markdown.markdown_decoration.quote(
                    f"Данный пользователь уже является аднимистратором"
                ),
                reply_markup=admin_admins_keyboard,
            )
        else:
            data["username"] = message.text.replace("@", "")
            data["telegram_id"] = telegram_id
            await orm_add_admin(session=session, data=data)
            await message.answer(
                text=markdown.markdown_decoration.quote(
                    f"Администратор успешно добавлен"
                ),
                reply_markup=admin_admins_keyboard,
            )
    else:
        await message.answer(
            text=markdown.markdown_decoration.quote(
                f"Такого пользователя не существует"
            ),
            reply_markup=admin_admins_keyboard,
        )
    await state.clear()
