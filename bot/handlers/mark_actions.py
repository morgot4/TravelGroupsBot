from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.utils import markdown
from aiogram.enums import ParseMode
from bot.utils.states import MarkActions
from sqlalchemy.ext.asyncio import AsyncSession
from bot.keyboards import admin_mark_keyboard, profile
from bot.keyboards.builders import get_callback_buttons
from bot.database.cruds import (
    orm_add_mark,
    orm_select_mark,
    orm_update_mark,
    orm_select_mark_by_phone_number,
)
from bot.utils.get_user import get_user
from bot.config import bot_manager
import phonenumbers
from phonenumbers import carrier
from phonenumbers.phonenumberutil import number_type

router = Router()


async def validate_mobile(number):
    return carrier._is_mobile(number_type(phonenumbers.parse(number)))


async def validate_user_id(bot: Bot, telegram_id: int, mark_code: str):
    try:
        await bot.send_message(
            chat_id=telegram_id,
            text=f"Вас назначали владельцем метки *{markdown.markdown_decoration.quote(mark_code)}*",
            parse_mode=ParseMode.MARKDOWN_V2,
        )
        return True
    except Exception as exp:
        return False


@router.message(MarkActions.mark_code, F.text == "\U0001f519 Назад")
async def back_mark_menu(message: Message, state: FSMContext):
    await message.answer(
        text=markdown.markdown_decoration.quote("Создание метки отменено"),
        reply_markup=admin_mark_keyboard,
    )
    await state.clear()


@router.message(MarkActions.mark_code, F.text)
async def mark_code(message: Message, state: FSMContext, session: AsyncSession):
    data = await state.get_data()
    data["mark_code"] = message.text.upper()
    data["captain_username"] = None
    data["captain_telegram_id"] = None
    data["captain_phone_number"] = None
    await orm_add_mark(session=session, data=data)
    await message.answer(
        text=markdown.markdown_decoration.quote(
            f"Метка {data['mark_code']} успешко добавлена"
        ),
        reply_markup=admin_mark_keyboard,
    )
    await state.clear()


@router.message(MarkActions.mark_code)
async def mark_code(message: Message, state: FSMContext):
    await message.answer(
        text=markdown.markdown_decoration.quote(
            "Кодом метки должен быть текст из букв и цифр. Попробуйте снова"
        ),
        reply_markup=profile(f"\U0001f519 Назад"),
    )


@router.message(MarkActions.fix_mark_code, F.text == "\U0001f519 Назад")
async def fix_mark_code(message: Message, state: FSMContext):
    await message.answer(
        text=markdown.markdown_decoration.quote("Изменение метки отменено"),
        reply_markup=admin_mark_keyboard,
    )
    await state.clear()


@router.message(MarkActions.fix_mark_code, F.text)
async def fix_mark_code(message: Message, state: FSMContext, session: AsyncSession):
    data = await state.get_data()
    previous_mark_code = data["mark_code"]
    mark = await orm_select_mark(session=session, mark_code=previous_mark_code)
    data["mark_code"] = message.text
    data["captain_username"] = mark.captain_username
    data["captain_telegram_id"] = mark.captain_telegram_id
    data["captain_phone_number"] = mark.captain_phone_number
    await orm_update_mark(session=session, mark=mark, data=data)
    await message.answer(
        text=markdown.markdown_decoration.quote(
            f"Новый код {data['mark_code']} установлен"
        ),
        reply_markup=admin_mark_keyboard,
    )
    await state.clear()


@router.message(MarkActions.fix_mark_owner_username, F.text)
async def fix_mark_owner_username(
    message: Message, state: FSMContext, session: AsyncSession
):
    new_username = message.text.replace("@", "")
    new_user = await get_user(new_username)
    data = await state.get_data()
    mark_code = data["mark_code"]
    if new_user is None:
        await message.answer(
            text=markdown.markdown_decoration.quote(
                f"Пользователь @{new_username} не найден. Попробуйте снова"
            ),
            reply_markup=profile(f"\U0001f519 Назад"),
        )
    else:
        new_telegram_id = new_user.full_user.id
        if await validate_user_id(
            bot_manager.get_bot(), new_telegram_id, mark_code=mark_code
        ):
            mark = await orm_select_mark(session=session, mark_code=mark_code)
            data["mark_code"] = mark_code
            data["captain_username"] = new_username
            data["captain_telegram_id"] = new_telegram_id
            data["captain_phone_number"] = mark.captain_phone_number
            await orm_update_mark(session=session, mark=mark, data=data)
            await message.answer(
                text=markdown.markdown_decoration.quote(
                    f"Новый пользователь @{data['captain_username']} установлен"
                ),
                reply_markup=admin_mark_keyboard,
            )
            await state.clear()
        else:
            await message.answer(
                text=markdown.markdown_decoration.quote(
                    f"Пользователь @{new_username} не писал боту. Невозможно установить его владельцем метки. Попробуйте снова"
                ),
                reply_markup=profile(f"\U0001f519 Назад"),
            )


@router.message(MarkActions.fix_mark_owner_phone, F.text)
async def fix_mark_owner_phone(
    message: Message, state: FSMContext, session: AsyncSession
):
    new_phone = message.text
    data = await state.get_data()
    mark_code = data["mark_code"]
    if new_phone[0] == "+":
        new_phone = "+7" + new_phone[2:]
    else:
        new_phone = "+7" + new_phone[1:]
    if await validate_mobile(new_phone):
        mark = await orm_select_mark(session=session, mark_code=mark_code)
        data["mark_code"] = mark_code
        data["captain_username"] = mark.captain_username
        data["captain_telegram_id"] = mark.captain_telegram_id
        data["captain_phone_number"] = new_phone
        await orm_update_mark(session=session, mark=mark, data=data)
        await message.answer(
            text=markdown.markdown_decoration.quote(
                f"Новый номер телефона {new_phone} установлен"
            ),
            reply_markup=admin_mark_keyboard,
        )
        await state.clear()
    else:
        await message.answer(
            text=markdown.markdown_decoration.quote(
                f"Неверный омер телефона. Проверьте правильность написания и попробуйте снова"
            ),
            reply_markup=profile(f"\U0001f519 Назад"),
        )


@router.message(MarkActions.mark_code)
async def back_mark_menu(message: Message, state: FSMContext):
    await message.answer(
        text=markdown.markdown_decoration.quote(
            "Кодом метки должен быть текст из букв и цифр. Попробуйте снова"
        ),
        reply_markup=profile(f"\U0001f519 Назад"),
    )


@router.message(MarkActions.find_mark_by_code, F.text == "\U0001f519 Назад")
async def find_mark_by_code(message: Message, state: FSMContext):
    await message.answer(
        text=markdown.markdown_decoration.quote("Поиск метки отменён"),
        reply_markup=admin_mark_keyboard,
    )
    await state.clear()


@router.message(MarkActions.find_mark_by_code)
async def find_mark_by_code(message: Message, state: FSMContext, session: AsyncSession):
    mark_code = message.text.upper()
    mark = await orm_select_mark(session=session, mark_code=mark_code)
    if mark is not None:
        await message.answer(
            text="Метка успешка найдена", reply_markup=admin_mark_keyboard
        )
        await message.answer(
            text=f"Метка: *{markdown.markdown_decoration.quote(mark.mark_code)}*",
            reply_markup=get_callback_buttons(
                buttons={"\U00002b07 Подробнее": f"more_about_mark_{mark.mark_code}"},
                size=(1,),
            ),
        )
        await state.clear()
    else:
        await message.answer(
            text=f"Метка *{markdown.markdown_decoration.quote(mark_code)}* не найдена\\. Попробуйте снова\\.",
            parse_mode=ParseMode.MARKDOWN_V2,
        )


@router.message(MarkActions.find_mark_by_phone_number, F.text == "\U0001f519 Назад")
async def find_mark_by_phone_number(message: Message, state: FSMContext):
    await message.answer(
        text=markdown.markdown_decoration.quote("Поиск метки отменён"),
        reply_markup=admin_mark_keyboard,
    )
    await state.clear()


@router.message(MarkActions.find_mark_by_phone_number)
async def find_mark_by_phone_number(
    message: Message, state: FSMContext, session: AsyncSession
):
    phone_number = message.text
    if phone_number[0] == "+":
        phone_number = "+7" + phone_number[2:]
    else:
        phone_number = "+7" + phone_number[1:]
    if await validate_mobile(phone_number):
        mark = await orm_select_mark_by_phone_number(
            session=session, phone_number=phone_number
        )
        if mark is not None:
            await message.answer(
                text="Метка успешка найдена", reply_markup=admin_mark_keyboard
            )
            await message.answer(
                text=f"Метка: *{markdown.markdown_decoration.quote(mark.mark_code)}*",
                reply_markup=get_callback_buttons(
                    buttons={
                        "\U00002b07 Подробнее": f"more_about_mark_{mark.mark_code}"
                    },
                    size=(1,),
                ),
            )
            await state.clear()
            return
        else:
            await message.answer(
                text=f"К номеру телефона *{markdown.markdown_decoration.quote(phone_number)}* не привязана ни одна метка\\. Попробуйте снова\\.",
                parse_mode=ParseMode.MARKDOWN_V2,
            )
    else:
        await message.answer(
            text=markdown.markdown_decoration.quote(
                f"Неверный омер телефона. Проверьте правильность написания и попробуйте снова"
            ),
            reply_markup=profile(f"\U0001f519 Назад"),
        )


@router.message(MarkActions.add_phone_to_mark)
async def add_phone_to_mark(message: Message, session: AsyncSession, state: FSMContext):
    phone_number = message.contact.phone_number
    telegram_id = message.from_user.id
    username = message.from_user.username
    data = await state.get_data()
    mark = await orm_select_mark(session=session, mark_code=data["mark_code"])
    data["captain_username"] = username
    data["captain_telegram_id"] = telegram_id
    data["captain_phone_number"] = phone_number
    await message.answer(
        markdown.markdown_decoration.quote(
            f"Теперь вы владелец метки {data["mark_code"]}"
        )
    )
    await orm_update_mark(session=session, data=data, mark=mark)
    await state.clear()
