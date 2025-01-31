from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, Message
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.utils import markdown
from sqlalchemy.ext.asyncio import AsyncSession
from bot.database.cruds import (
    orm_select_mark,
    orm_delete_mark,
    orm_select_admin,
    orm_delete_admin,
)
from bot.keyboards.builders import get_callback_buttons, profile
from bot.keyboards import admin_mark_keyboard, allow_contact, rmk
from bot.utils.states import MarkActions
from bot.utils.marks_actions import clear_all_marks


router = Router()


@router.callback_query(F.data.startswith("more_about_mark_"))
async def more_about_mark(callback: CallbackQuery, session: AsyncSession):
    mark_code = "_".join(callback.data.split("_")[3:])
    mark = await orm_select_mark(session=session, mark_code=mark_code)
    if mark.captain_username is not None:
        new_text = (
            markdown.markdown_decoration.quote(f"\nТелеграмм: @{mark.captain_username}")
            + f"\nТелефон: `{mark.captain_phone_number}`"
        )
    else:
        new_text = markdown.markdown_decoration.quote(f"\nТелеграмм: -\nТелефон: -")

    await callback.message.edit_text(
        text=f"Метка: *{markdown.markdown_decoration.quote(mark.mark_code)}*"
        + new_text,
        parse_mode=ParseMode.MARKDOWN_V2,
        reply_markup=get_callback_buttons(
            buttons={
                "\U0001f6e0 Изменить": f"fix_mark_{mark_code}",
                "\U0001f5d1 Удалить": f"delete_mark_{mark_code}",
                "\U00002b06 Скрыть": f"less_about_mark_{mark_code}",
            },
            size=(
                2,
                1,
            ),
        ),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("less_about_mark_"))
async def less_about_mark(callback: CallbackQuery):
    mark_code = "_".join(callback.data.split("_")[3:])
    await callback.message.edit_text(
        text=f"Метка: *{markdown.markdown_decoration.quote(mark_code)}*",
        parse_mode=ParseMode.MARKDOWN_V2,
        reply_markup=get_callback_buttons(
            buttons={"\U00002b07 Подробнее": f"more_about_mark_{mark_code}"}, size=(1,)
        ),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("delete_mark_"))
async def delete_mark(callback: CallbackQuery, session: AsyncSession):
    mark_code = "_".join(callback.data.split("_")[2:])
    mark = await orm_select_mark(session=session, mark_code=mark_code)
    await callback.message.delete()
    await callback.answer()
    await orm_delete_mark(session=session, mark=mark)


@router.callback_query(F.data.startswith("fix_mark_"))
async def fix_mark(callback: CallbackQuery, session: AsyncSession):
    mark_code = "_".join(callback.data.split("_")[2:])
    await callback.message.edit_text(
        text=markdown.markdown_decoration.quote(callback.message.text),
        parse_mode=ParseMode.MARKDOWN_V2,
        reply_markup=get_callback_buttons(
            buttons={
                "\U0001f511 Изменить код метки": f"fix_code_mark_{mark_code}",
                "\U0001f6b9 Изменить владельца": f"fix_owner_mark_{mark_code}",
                "\U00002b06 Скрыть": f"less_about_mark_{mark_code}",
            },
            size=(
                1,
                1,
                1,
            ),
        ),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("fix_code_mark_"))
async def fix_code_mark_(callback: CallbackQuery, state: FSMContext):
    mark_code = "_".join(callback.data.split("_")[3:])
    await state.set_state(MarkActions.fix_mark_code)
    await state.set_data({"mark_code": mark_code})
    await callback.message.answer(
        markdown.markdown_decoration.quote("Введите новый код метки"),
        reply_markup=profile("\U0001f519 Назад"),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("fix_owner_mark_"))
async def fix_owner_mark_(callback: CallbackQuery):
    mark_code = "_".join(callback.data.split("_")[3:])
    await callback.message.edit_text(
        text=markdown.markdown_decoration.quote(callback.message.text),
        parse_mode=ParseMode.MARKDOWN_V2,
        reply_markup=get_callback_buttons(
            buttons={
                "\U0001faaa Изменить телеграмм ": f"fix_owner_telegram_mark_{mark_code}",
                "\U0000260e Изменить номер телефона": f"fix_owner_phone_mark_{mark_code}",
                "\U00002b06 Скрыть": f"less_about_mark_{mark_code}",
            },
            size=(
                1,
                1,
                1,
            ),
        ),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("fix_owner_telegram_mark_"))
async def fix_owner_telegram_mark_(callback: CallbackQuery, state: FSMContext):
    mark_code = "_".join(callback.data.split("_")[4:])
    await state.set_state(MarkActions.fix_mark_owner_username)
    await state.set_data({"mark_code": mark_code})
    await callback.message.answer(
        markdown.markdown_decoration.quote(
            "Введите новое имя пользователя (telegram username)"
        ),
        reply_markup=profile("\U0001f519 Назад"),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("fix_owner_phone_mark_"))
async def fix_owner_phone_mark_(callback: CallbackQuery, state: FSMContext):
    mark_code = "_".join(callback.data.split("_")[4:])
    await state.set_state(MarkActions.fix_mark_owner_phone)
    await state.set_data({"mark_code": mark_code})
    await callback.message.answer(
        markdown.markdown_decoration.quote("Введите новый номер телефона"),
        reply_markup=profile("\U0001f519 Назад"),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("yes_clear"))
async def yes_clear_all_marks(callback: CallbackQuery, session: AsyncSession):
    await callback.message.answer(
        "Метки успешно обновлены", reply_markup=admin_mark_keyboard
    )
    await callback.answer()
    await clear_all_marks(message=callback.message, session=session)


@router.callback_query(F.data.startswith("no_clear"))
async def no_clear_all_marks(callback: CallbackQuery):
    await callback.message.answer("Отмена обновления", reply_markup=admin_mark_keyboard)
    await callback.answer()


@router.callback_query(F.data.startswith("yes_add_mark"))
async def yes_clear_all_marks(
    callback: CallbackQuery, session: AsyncSession, state: FSMContext
):
    await state.set_state(MarkActions.add_phone_to_mark)
    await callback.message.answer(
        "Требуется номер телефона", reply_markup=allow_contact
    )
    await callback.answer()


@router.callback_query(F.data.startswith("no_add_mark"))
async def no_clear_all_marks(callback: CallbackQuery):
    await callback.message.answer("Присвоение метки отменено", reply_markup=rmk)
    await callback.answer()


@router.callback_query(F.data.startswith("delete_admin_"))
async def delete_admin(callback: CallbackQuery, session: AsyncSession):
    telegram_id = "_".join(callback.data.split("_")[2:])
    admin = await orm_select_admin(session=session, telegram_id=int(telegram_id))
    if admin is not None:
        await callback.message.delete()
        await orm_delete_admin(session=session, admin=admin)
    else:
        await callback.message.answer(
            "Администратора уже не существует, обновите список", reply_markup=rmk
        )
    await callback.answer()
