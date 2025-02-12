from aiogram import Router
from aiogram.types import Message, ContentType
from aiogram.filters import Command
from aiogram.utils import markdown
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from bot.database.cached_cruds import get_cached_admin, get_cached_mark

# from bot.database.cruds import (
#     orm_select_admin,
#     orm_select_mark,
#     orm_select_mark_by_telegram_id,
# )
from bot.keyboards import (
    admin_start_menu,
    admin_mark_keyboard,
    admin_admins_keyboard,
    admin_point_keyboard,
    profile,
    rmk,
)
from bot.keyboards.builders import get_callback_buttons
from bot.utils.states import MarkActions, AdminActions, PointAction
from bot.utils.marks_actions import get_all_marks, check_all_marks
from bot.utils.admins_action import get_all_admins
from bot.utils.points_action import get_all_points

router = Router()


@router.message(Command("start"))
async def start(message: Message, session: AsyncSession):
    if message.chat.type in ["group", "supergroup"]:
        return

    user_id = message.from_user.id

    user_mark = await get_cached_mark(
        session=session, key=str(user_id), find_by="telegram_id", delete=False
    )
    admin = await get_cached_admin(
        session=session, admin_telegram_id=str(user_id), delete=False
    )
    if admin is not None:
        await message.answer(
            text=markdown.markdown_decoration.quote(
                f"Здравствуйте, {message.from_user.first_name}. Вы зашли от имени администратора. "
            ),
            reply_markup=admin_start_menu,
        )

    else:
        await message.answer(
            text=markdown.markdown_decoration.quote(
                """Здравствуйте!
Вы находитесь в приложении Tourists Manager - «Контроль туристских групп на маршруте».
Нажмите кнопку «Меню» в правом нижнем углу появится - «Labels», нажмите.
В открывшееся поле внесите номер полученной МЕТКИ. 
Шрифт - ЛАТИНСКИЙ, буквы - ЗАГЛАВНЫЕ, без пробелов.
В случае если метка свободна, Вам будет предложено присвоить МЕТКУ.
Нажмите кнопку «ДА».
Далее в левом нижнем углу нажмите на кнопку 
«Представить номер телефона».
Далее - «Поделиться контактом».
Если ваши действия верны, Вы станете владельцем метки."""
            )
        )

@router.message(Command("labels"))
async def start(message: Message, session: AsyncSession):
    if message.chat.type in ["group", "supergroup"]:
        return

    user_id = message.from_user.id

    user_mark = await get_cached_mark(
        session=session, key=str(user_id), find_by="telegram_id", delete=False
    )
    if user_mark is not None:
        await message.answer(
            text=markdown.markdown_decoration.quote(
                f"Ваша метка: {user_mark.mark_code} \n Последняя позиция: {'Точка #'+ str(user_mark.last_point) if user_mark.last_point is not None else "-"}"
            )
        )
    else:
        await message.answer(
            text=markdown.markdown_decoration.quote(
                f"Введите код метки",
            ),
        )
@router.message()
async def main(message: Message, session: AsyncSession, state: FSMContext):
    if message.chat.type in ["group", "supergroup"]:
        return
    user_id = message.from_user.id
    user_mark = await get_cached_mark(
        session=session, key=str(user_id), find_by="telegram_id", delete=False
    )
    text = message.text
    admin = await get_cached_admin(
        session=session, admin_telegram_id=str(user_id), delete=False
    )
    mark_orm = await get_cached_mark(session=session, key=text.upper(), delete=False)
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

        elif text == "\U0001f4cc Маяки":
            await message.answer(
                text=markdown.markdown_decoration.quote(
                    "Выберите взаимодействие с маяками"
                ),
                reply_markup=admin_point_keyboard,
            )

        elif text == "\U00002795 Добавить метку":
            await message.answer(
                text=markdown.markdown_decoration.quote(f"Введите код метки"),
                reply_markup=profile(f"\U0001f519 Назад"),
            )
            await state.set_state(MarkActions.mark_code)

        elif text == "\U00002795 Добавить маяк":
            await message.answer(
                text=markdown.markdown_decoration.quote(f"Введите номер маяка"),
                reply_markup=profile(f"\U0001f519 Назад"),
            )
            await state.set_state(PointAction.add_point)

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

        elif text == "\U0001f4c3 Список всех маяков":
            await message.answer(
                text=markdown.markdown_decoration.quote(f"Все маяки ->"),
                reply_markup=admin_point_keyboard,
            )
            await get_all_points(message=message, session=session)

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

        elif text == "\U0001f50d Найти маяк (номер)":
            await message.answer(
                text="Введите номер маяка", reply_markup=profile(f"\U0001f519 Назад")
            )
            await state.set_state(PointAction.find_point_by_number)

        elif text == "\U0001f50d Найти метку (номер телефона)":
            await message.answer(
                text="Введите номер телефона", reply_markup=profile(f"\U0001f519 Назад")
            )
            await state.set_state(MarkActions.find_mark_by_phone_number)

        elif text == "\U0001f4de Проверка всех меток":
            await message.answer(text="Тестовое сообщение было отправлено всем меткам")
            bad_marks = await check_all_marks(session=session)
            if bad_marks == []:
                await message.answer(text="У каждой метки есть владелец")
            else:
                await message.answer(
                    text=f"Незанятые метки: {', '.join([code for code in bad_marks])}"
                )

        else:
            await message.answer(
                text=markdown.markdown_decoration.quote(
                    f"Здравствуйте, {message.from_user.first_name}. Вы зашли от имени администратора"
                ),
                reply_markup=admin_start_menu,
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
