from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

admin_start_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="\U0001f4cd Метки")],
        [KeyboardButton(text="\U0001f4cc Маяки")],
        [KeyboardButton(text="\U0001faaa Администраторы")],
    ],
    resize_keyboard=True,
    one_time_keyboard=True,
    input_field_placeholder="Выберите действие",
)

admin_mark_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="\U0001f50d Найти метку (код)"),
            KeyboardButton(text="\U0001f50d Найти метку (номер телефона)"),
        ],
        [
            KeyboardButton(text="\U00002795 Добавить метку"),
            KeyboardButton(text="\U000026a0 Очистка всех меток \U000026a0"),
        ],
        [
            KeyboardButton(text="\U0001f4de Проверка всех меток"),
            KeyboardButton(text="\U0001f4c3 Список всех меток"),
        ],
        # [KeyboardButton(text="Отправить капитанам")],
        [KeyboardButton(text="\U0001f519 Назад")],
    ],
    resize_keyboard=True,
    one_time_keyboard=False,
    input_field_placeholder="Выберите действие",
)

admin_point_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="\U0001f50d Найти маяк (номер)"),
        ],
        [
            KeyboardButton(text="\U00002795 Добавить маяк"),
        ],
        [
            KeyboardButton(text="\U0001f4c3 Список всех маяков"),
        ],
        [KeyboardButton(text="\U0001f519 Назад")],
    ],
    resize_keyboard=True,
    one_time_keyboard=False,
    input_field_placeholder="Выберите действие",
)

admin_admins_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="\U00002795 Добавить администратора"),
            KeyboardButton(text="\U0001f4c3 Список администраторов"),
        ],
        [KeyboardButton(text="\U0001f519 Назад")],
    ],
    resize_keyboard=True,
    one_time_keyboard=False,
    input_field_placeholder="Выберите действие",
)

allow_contact = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(
                text="\U0000260e Предоставить номер телефона", request_contact=True
            ),
            KeyboardButton(text="\U0001f4f5 Отмена"),
        ]
    ],
    resize_keyboard=True,
    one_time_keyboard=True,
)


rmk = ReplyKeyboardRemove()
