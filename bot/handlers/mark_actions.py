from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.utils import markdown
from aiogram.enums import ParseMode
from bot.utils.states import MarkActions
from sqlalchemy.ext.asyncio import AsyncSession
from bot.keyboards import admin_mark_keyboard, profile, rmk
from bot.keyboards.builders import get_callback_buttons
from bot.database.cached_cruds import get_cached_mark
from bot.database.cruds import orm_add_mark, orm_update_mark, orm_select_points
from bot.utils.telegram_client import get_user
from bot.config import bot_manager
import phonenumbers
from phonenumbers import carrier
from phonenumbers.phonenumberutil import number_type

router = Router()


async def validate_mobile(number):
    if number[0] == "+":
        number = "+7" + number[2:]
    else:
        number = "+7" + number[1:]
    if carrier._is_mobile(number_type(phonenumbers.parse(number))):
        return True, number
    return False


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
    data["history"] = []
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
    mark = await get_cached_mark(session=session, key=previous_mark_code, delete=True)
    if mark is not None:
        data["mark_code"] = message.text
        data["captain_username"] = mark.captain_username
        data["captain_telegram_id"] = mark.captain_telegram_id
        data["captain_phone_number"] = mark.captain_phone_number
        data["history"] = mark.history
        await orm_update_mark(session=session, mark=mark, data=data)
        await message.answer(
            text=markdown.markdown_decoration.quote(
                f"Новый код {data['mark_code']} установлен"
            ),
            reply_markup=admin_mark_keyboard,
        )
        await state.clear()
    else:
        await message.answer(
            text=markdown.markdown_decoration.quote(
                f"Такой метки не существует, обновите список."
            ),
            reply_markup=admin_mark_keyboard,
        )



@router.message(MarkActions.fix_mark_owner_username, F.text)
async def fix_mark_owner_username(
    message: Message, state: FSMContext, session: AsyncSession
):
    new_username = message.text.replace("@", "")
    new_user = await get_user(new_username, client=bot_manager.get_client())
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
            mark = await get_cached_mark(session=session, key=mark_code, delete=True)
            data["mark_code"] = mark_code
            data["captain_username"] = new_username
            data["captain_telegram_id"] = str(new_telegram_id)
            data["captain_phone_number"] = mark.captain_phone_number
            data["history"] = mark.history
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

    is_valid, new_phone = await validate_mobile(new_phone)
    if is_valid:
        mark = await get_cached_mark(session=session, key=mark_code, delete=True)
        data["mark_code"] = mark_code
        data["captain_username"] = mark.captain_username
        data["captain_telegram_id"] = mark.captain_telegram_id
        data["captain_phone_number"] = new_phone
        data["history"] = mark.history
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
    mark = await get_cached_mark(session=session, key=mark_code, delete=False)
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
    is_valid, phone_number = await validate_mobile(phone_number)
    if is_valid:
        mark = await get_cached_mark(
            session=session, key=phone_number, find_by="phone", delete=False
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
                f"Неверный номер телефона. Проверьте правильность написания и попробуйте снова"
            ),
            reply_markup=profile(f"\U0001f519 Назад"),
        )

@router.message(MarkActions.add_phone_to_mark, F.text == "\U0001f4f5 Отмена")
async def cancel_add_phone(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
            text=markdown.markdown_decoration.quote(
                "Чтобы присвоить метку необходимо предоставить номер телефона. Введите код метки еще раз"
            ),
            reply_markup=rmk,
        )

@router.message(MarkActions.add_phone_to_mark)
async def add_phone_to_mark(message: Message, session: AsyncSession, state: FSMContext):
    phone_number = message.contact.phone_number
    telegram_id = str(message.from_user.id)
    username = message.from_user.username
    is_valid, phone_number = await validate_mobile(phone_number)
    data = await state.get_data()
    mark = await get_cached_mark(session=session, key=data["mark_code"], delete=True)
    data["captain_username"] = username
    data["captain_telegram_id"] = telegram_id
    data["captain_phone_number"] = phone_number
    data["history"] = mark.history
    await message.answer(
        markdown.markdown_decoration.quote(
            f"Теперь вы владелец метки {data["mark_code"]}",
        ),
        reply_markup=rmk,
    )
    await orm_update_mark(session=session, data=data, mark=mark)
    await state.clear()
