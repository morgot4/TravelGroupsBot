from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.utils import markdown
from aiogram.enums import ParseMode
from bot.utils.states import PointAction
from sqlalchemy.ext.asyncio import AsyncSession
from bot.keyboards import admin_point_keyboard, profile, rmk
from bot.keyboards.builders import get_callback_buttons
from bot.database.cached_cruds import get_cached_point, add_cached_point
from bot.database.cruds import orm_add_point, orm_update_point
from bot.utils.telegram_client import get_user
from bot.config import bot_manager


router = Router()


@router.message(PointAction.add_point, F.text == "\U0001f519 Назад")
async def back_point_menu(message: Message, state: FSMContext):
    await message.answer(
        text=markdown.markdown_decoration.quote("Создание маяка отменено"),
        reply_markup=admin_point_keyboard,
    )
    await state.clear()


@router.message(PointAction.add_point)
async def add_point(message: Message, state: FSMContext, session: AsyncSession):
    number = message.text
    if number.isdigit():
        data = {"number": int(number), "text": ""}
        await orm_add_point(session=session, data=data)
        await message.answer(
            text=markdown.markdown_decoration.quote("Маяк создан"),
            reply_markup=admin_point_keyboard,
        )
    else:
        await message.answer(
            text=markdown.markdown_decoration.quote("Номер должен быть числом"),
            reply_markup=admin_point_keyboard,
        )
    await state.clear()


@router.message(PointAction.find_point_by_number)
async def find_point_by_number(message: Message, state: FSMContext, session: AsyncSession):
    number = message.text
    if number.isdigit():
        point = await get_cached_point(session=session, number=int(number), delete=False)
        if point is not None:
            await message.answer(
                text=markdown.markdown_decoration.quote("Маяк успешно найден"),
                reply_markup=admin_point_keyboard,
            )
            await message.answer(
                text=f"Точка *\\#{markdown.markdown_decoration.quote(str(point.number))}*",
                reply_markup=get_callback_buttons(
                    buttons={"\U00002b07 Подробнее": f"more_about_point_{point.number}"},
                    size=(1,),
                ),
                parse_mode=ParseMode.MARKDOWN_V2,
            )
        else:
            await message.answer(
                text=markdown.markdown_decoration.quote("Маяка с таким номером не существует"),
                reply_markup=admin_point_keyboard,
            )
    else:
        await message.answer(
                text=markdown.markdown_decoration.quote("Номер должен быть числом"),
                reply_markup=admin_point_keyboard,
            )
    await state.clear()


@router.message(PointAction.fix_point_number, F.text == "\U0001f519 Назад")
async def back_to_point_menu(message: Message, state: FSMContext):
    await message.answer(
        text=markdown.markdown_decoration.quote("Изменение маяка отменено"),
        reply_markup=admin_point_keyboard,
    )
    await state.clear()


@router.message(PointAction.fix_point_number, F.text)
async def fix_point_number(message: Message, state: FSMContext, session: AsyncSession):
    data = await state.get_data()
    previous_number = data["number"]
    point = await get_cached_point(session=session, number=previous_number, delete=True)
    if point is not None:
        if message.text.isdigit():
            data["number"] = int(message.text)
            data["text"] = point.text
            await orm_update_point(session=session, point=point, data=data)
            await message.answer(
                text=markdown.markdown_decoration.quote(
                    f"Новый номер {data['number']} установлен"
                ),
                reply_markup=admin_point_keyboard,
            )
        else:
            await message.answer(
            text=markdown.markdown_decoration.quote(
                f"Номером метки должно быть число"
            ),
            reply_markup=admin_point_keyboard,
        )
            
    else:
        await message.answer(
            text=markdown.markdown_decoration.quote(
                f"Такой метки не существует, обновите список."
            ),
            reply_markup=admin_point_keyboard,
        )
    await state.clear()



@router.message(PointAction.fix_point_text, F.text == "\U0001f519 Назад")
async def back_to_point_menu(message: Message, state: FSMContext):
    await message.answer(
        text=markdown.markdown_decoration.quote("Изменение маяка отменено"),
        reply_markup=admin_point_keyboard,
    )
    await state.clear()

@router.message(PointAction.fix_point_text)
async def fix_point_text(message: Message, state: FSMContext, session: AsyncSession):
    data = await state.get_data()
    number = data["number"]
    data["text"] = message.text
    point = await get_cached_point(session=session, number=number, delete=True)
    await orm_update_point(session=session, point=point, data=data)
    await message.answer(
        text=markdown.markdown_decoration.quote(
            f"Новый текст установлен"
        ),
        reply_markup=admin_point_keyboard,
    )
    await state.clear()