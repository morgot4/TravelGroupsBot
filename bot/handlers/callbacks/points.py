from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.utils import markdown
from sqlalchemy.ext.asyncio import AsyncSession
from bot.database.cached_cruds import (

    get_cached_point,
)
from bot.database.cruds import orm_delete_point
from bot.keyboards.builders import get_callback_buttons
from bot.keyboards import admin_mark_keyboard, allow_contact, rmk, profile
from bot.utils.states import PointAction


router = Router()



@router.callback_query(F.data.startswith("more_about_point_"))
async def more_about_point(callback: CallbackQuery, session: AsyncSession):
    number = "_".join(callback.data.split("_")[3:])
    point = await get_cached_point(session=session, number=int(number), delete=False)
    new_text = f"Точка *\\#{markdown.markdown_decoration.quote(str(point.number))}*\nТекст\\: {point.text}"

    await callback.message.edit_text(
        text=new_text,
        parse_mode=ParseMode.MARKDOWN_V2,
        reply_markup=get_callback_buttons(
            buttons={
                "\U0001f6e0 Изменить": f"fix_point_{number}",
                "\U0001f5d1 Удалить": f"delete_point_{number}",
                "\U00002b06 Скрыть": f"less_about_point_{number}",
            },
            size=(
                2,
                1,
            ),
        ),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("less_about_point_"))
async def less_about_mark(callback: CallbackQuery):
    number = "_".join(callback.data.split("_")[3:])
    await callback.message.edit_text(
        text=f"Точка *\\#{markdown.markdown_decoration.quote(number)}*",
        parse_mode=ParseMode.MARKDOWN_V2,
        reply_markup=get_callback_buttons(
            buttons={"\U00002b07 Подробнее": f"more_about_point_{number}"}, size=(1,)
        ),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("delete_point_"))
async def delete_point(callback: CallbackQuery, session: AsyncSession):
    number = "_".join(callback.data.split("_")[2:])
    point = await get_cached_point(session=session, number=int(number), delete=True)
    await callback.message.delete()
    await callback.answer()
    await orm_delete_point(session=session, number=int(number))



@router.callback_query(F.data.startswith("fix_point_"))
async def fix_point(callback: CallbackQuery):
    number = "_".join(callback.data.split("_")[2:])
    await callback.message.edit_text(
        text=markdown.markdown_decoration.quote(callback.message.text),
        parse_mode=ParseMode.MARKDOWN_V2,
        reply_markup=get_callback_buttons(
            buttons={
                "\U0001F3F7 Изменить номер маяка": f"fix_number_point_{number}",
                "\U0001F4C4 Изменить текст": f"fix_text_point_{number}",
                "\U00002b06 Скрыть": f"less_about_point_{number}",
            },
            size=(
                1,
                1,
                1,
            ),
        ),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("fix_number_point_"))
async def fix_number_point(callback: CallbackQuery, state: FSMContext):
    number = "_".join(callback.data.split("_")[3:])
    await state.set_state(PointAction.fix_point_number)
    await state.set_data({"number": int(number)})
    await callback.message.answer(
        markdown.markdown_decoration.quote("Введите новый номер маяка"),
        reply_markup=profile("\U0001f519 Назад"),
    )
    await callback.answer()



@router.callback_query(F.data.startswith("fix_text_point_"))
async def fix_text_point(callback: CallbackQuery, state: FSMContext):
    number = "_".join(callback.data.split("_")[3:])
    await state.set_state(PointAction.fix_point_text)
    await state.set_data({"number": int(number)})
    await callback.message.answer(
        markdown.markdown_decoration.quote("Введите новый текст для маяка"),
        reply_markup=profile("\U0001f519 Назад"),
    )
    await callback.answer()