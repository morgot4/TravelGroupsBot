from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.utils import markdown
from sqlalchemy.ext.asyncio import AsyncSession
from bot.database.cached_cruds import (
    get_cached_mark,
)
from bot.database.cruds import orm_delete_mark, orm_update_mark
from bot.keyboards.builders import get_callback_buttons, profile
from bot.keyboards import admin_mark_keyboard, allow_contact, rmk
from bot.utils.states import MarkActions
from bot.utils.marks_actions import clear_all_marks, clear_mark


router = Router()


@router.callback_query(F.data.startswith("more_about_mark_"))
async def more_about_mark(callback: CallbackQuery, session: AsyncSession):
    mark_code = "_".join(callback.data.split("_")[3:])
    mark = await get_cached_mark(session=session, key=mark_code, delete=False)
    if mark.captain_username is not None:
        new_text = (
            markdown.markdown_decoration.quote(f"\nТелеграмм: @{mark.captain_username}")
            + f"\nТелефон: `{mark.captain_phone_number}`" + f"\nМаршрут: {"\\-" if mark.history is None else " \\> ".join(list(map(str, mark.history)))}"
        )
    else:
        new_text = markdown.markdown_decoration.quote(f"\nТелеграмм: -\nТелефон: -\nТочка: -")

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
    mark = await get_cached_mark(session=session, key=mark_code, delete=True)
    await callback.message.delete()
    await callback.answer()
    await orm_delete_mark(session=session, mark_code=mark.mark_code)


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
                "\U000026a0 Сбросить историю маршрута": f"drop_mark_history_{mark_code}",
                "\U000026a0 Очистить метку \U000026a0": f"clear_mark_{mark_code}",
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


@router.callback_query(F.data.startswith("drop_mark_history_"))
async def drop_point_mark_(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    mark_code = "_".join(callback.data.split("_")[3:])
    data = await state.get_data()
    mark = await get_cached_mark(session=session, key=mark_code, delete=True)
    if mark is not None:
        data["captain_username"] = mark.captain_username
        data["captain_telegram_id"] = mark.captain_telegram_id
        data["captain_phone_number"] = mark.captain_phone_number
        data["history"] = []
        await orm_update_mark(session=session, mark=mark, data=data)
        await callback.message.answer(
            text=markdown.markdown_decoration.quote(
                f"История сброшена"
            ),
            reply_markup=admin_mark_keyboard,
        )
    else:
        await callback.message.answer(
            text=markdown.markdown_decoration.quote(
                f"Такой метки не существует, обновите список."
            ),
            reply_markup=admin_mark_keyboard,
        )
    await callback.answer()


@router.callback_query(F.data.startswith("clear_mark_"))
async def clear_mark_info(callback: CallbackQuery, session: AsyncSession):
    mark_code = "_".join(callback.data.split("_")[2:])
    mark = await get_cached_mark(session=session, key=mark_code, delete=True)
    await clear_mark(mark=mark, session=session)
    await callback.message.edit_text(
        text=f"Метка: *{markdown.markdown_decoration.quote(mark_code)}*",
        parse_mode=ParseMode.MARKDOWN_V2,
        reply_markup=get_callback_buttons(
            buttons={"\U00002b07 Подробнее": f"more_about_mark_{mark_code}"}, size=(1,)
        ),
    )
    await callback.message.answer(
        text="Метка обновлена",
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
    await clear_all_marks(session=session)


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
        "ЖМИ НА \U0000260e предоставить номер ", reply_markup=allow_contact
    )
    await callback.answer()


@router.callback_query(F.data.startswith("no_add_mark"))
async def no_clear_all_marks(callback: CallbackQuery):
    await callback.message.answer("Присвоение метки отменено", reply_markup=rmk)
    await callback.answer()