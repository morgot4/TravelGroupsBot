from aiogram import Router
from aiogram.types import Message, ContentType
from aiogram.filters import Command
from aiogram.utils import markdown
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from bot.database.cruds import (
    orm_select_admin,
    orm_select_mark,
    orm_select_mark_by_telegram_id,
)
from bot.keyboards import (
    admin_start_menu,
    get_confirmation_menu,
    admin_mark_keyboard,
    admin_admins_keyboard,
    profile,
    rmk,
)
from bot.keyboards.builders import get_callback_buttons
from bot.utils.states import MarkActions, AdminActions
from bot.utils.marks_actions import get_all_marks, check_all_marks
from bot.utils.admins_action import get_all_admins


router = Router()


@router.message(Command("start"))
async def start(message: Message, session: AsyncSession):
    if message.chat.type in ["group", "supergroup"]:
        return
     
    user_id = message.from_user.id

    user_mark = await orm_select_mark_by_telegram_id(
        session=session, telegram_id=user_id
    )
    admin = await orm_select_admin(session=session, telegram_id=user_id)
    if admin is not None:
        await message.answer(
                text=markdown.markdown_decoration.quote(
                    f"Здравствуйте, {message.from_user.first_name}. Вы зашли от имени администратора. "
                ),
                reply_markup=admin_start_menu,
            )
    
    elif user_mark is None:
        await message.answer(
            "У вас нет меток\\. Пришлите *код*", parse_mode=ParseMode.MARKDOWN_V2
        )
    else:
        await message.answer(
            f"Ваша метка\\: *{user_mark.mark_code}*", parse_mode=ParseMode.MARKDOWN_V2
        )


@router.message()
async def main(message: Message, session: AsyncSession, state: FSMContext):
    text = message.text
    if message.chat.type in ["group", "supergroup"]:
        print(text.split())
        if "местоположение" in text.split():
            print(message)
            print(message.from_user)
        return
    
    user_id = message.from_user.id
    admin = await orm_select_admin(session=session, telegram_id=user_id)
    mark_orm = await orm_select_mark(session=session, mark_code=text.upper())
    user_mark = await orm_select_mark_by_telegram_id(
        session=session, telegram_id=user_id
    )

    if admin is not None:
        if text == "\U0001f4cd Метки":
            await message.answer(
                text=markdown.markdown_decoration.quote(
                    "Выберите взаимодействие с метками"
                ),
                reply_markup=admin_mark_keyboard,
            )

        elif text == "\U0001faaa Администраторы":
            await message.answer(
                text=markdown.markdown_decoration.quote(
                    "Выберите взаимодействие с администраторами"
                ),
                reply_markup=admin_admins_keyboard,
            )

        elif text == "\U00002795 Добавить метку":
            await message.answer(
                text=markdown.markdown_decoration.quote(f"Введите код метки"),
                reply_markup=profile(f"\U0001f519 Назад"),
            )
            await state.set_state(MarkActions.mark_code)

        elif text == "\U00002795 Добавить администратора":
            await message.answer(
                text=markdown.markdown_decoration.quote(
                    f"Введите имя пользователя (telegram username)"
                ),
                reply_markup=profile(f"\U0001f519 Назад"),
            )
            await state.set_state(AdminActions.add_admin)

        elif text == f"\U000026a0 Очистка всех меток \U000026a0":
            await message.answer(
                text=markdown.markdown_decoration.quote(
                    f"Вы уверены, что хотите сбросить информацию о владельцах?"
                ),
                reply_markup=get_callback_buttons(
                    buttons={
                        "\U00002705 Да ": "yes_clear",
                        "\U0000274c Нет": "no_clear",
                    },
                    size=(2,),
                ),
            )

        elif text == f"\U0001f4c3 Список всех меток":
            await message.answer(
                text=markdown.markdown_decoration.quote(f"Все метки ->"),
                reply_markup=admin_mark_keyboard,
            )
            await get_all_marks(message=message, session=session)

        elif text == "\U0001f4c3 Список администраторов":
            await message.answer(
                text=markdown.markdown_decoration.quote(f"Все aдминистраторы ->"),
                reply_markup=admin_admins_keyboard,
            )
            await get_all_admins(message=message, session=session)

        elif text == "\U0001f50d Найти метку (код)":
            await message.answer(
                text="Введите *код* метки", reply_markup=profile(f"\U0001f519 Назад")
            )
            await state.set_state(MarkActions.find_mark_by_code)

        elif text == "\U0001f50d Найти метку (номер телефона)":
            await message.answer(
                text="Введите номер телефона", reply_markup=profile(f"\U0001f519 Назад")
            )
            await state.set_state(MarkActions.find_mark_by_phone_number)

        elif text == "\U0001f4de Проверка всех меток":
            await message.answer(text="Тестовое сообщение было отправлено всем меткам")
            bad_marks = await check_all_marks(message=message, session=session)
            if bad_marks == []:
                await message.answer(text="У каждой метки есть владелец")
            else:
                await message.answer(text=f"Незанятые метки: {','.join([code for code in bad_marks])}")

        else:
            await message.answer(
                text=markdown.markdown_decoration.quote(
                    f"Здравствуйте, {message.from_user.first_name}. Вы зашли от имени администратора"
                ),
                reply_markup=admin_start_menu,
            )
    elif text == "\U0001f4f5 Отмена":
        await state.clear()
        await message.answer(
            text=markdown.markdown_decoration.quote(
                "Чтобы присвоить метку необходимо предоставить номер телефона. Введите код метки еще раз"
            ),
            reply_markup=rmk,
        )

    elif (
        mark_orm is not None
        and mark_orm.captain_telegram_id is None
        and user_mark is None
    ):
        await message.answer(
            text=markdown.markdown_decoration.quote(
                f"Метка {mark_orm.mark_code} свободна для записи. Присвоить вам эту метку?"
            ),
            reply_markup=get_callback_buttons(
                buttons={
                    "\U00002705 Да ": "yes_add_mark",
                    "\U0000274c Нет": "no_add_mark",
                },
                size=(2,),
            ),
        )
        await state.set_state(MarkActions.add_user_to_mark)
        await state.set_data({"mark_code": mark_orm.mark_code})

    elif mark_orm is None and user_mark is None:
        await message.answer(
            text=markdown.markdown_decoration.quote(
                f"Такой метки не существует. Проверьте, правильно ли вы написали код, попробуйте снова."
            )
        )

    elif (
        mark_orm is not None
        and mark_orm.captain_telegram_id is not None
        and mark_orm is None
    ):
        await message.answer(
            text=markdown.markdown_decoration.quote(
                f"Метка {mark_orm.mark_code} уже принадлежит другой командe. Пришлите код новой метки."
            )
        )

    elif user_mark is not None:
        await message.answer(
            text=f"У вас уже есть метка\\. Код\\: *{user_mark.mark_code}*",
            parse_mode=ParseMode.MARKDOWN_V2,
        )
