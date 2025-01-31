from aiogram.fsm.state import State, StatesGroup


class MarkActions(StatesGroup):
    mark_code = State()
    add_user_to_mark = State()
    add_phone_to_mark = State()
    find_mark_by_code = State()
    find_mark_by_phone_number = State()
    fix_mark_code = State()
    fix_mark_owner_username = State()
    fix_mark_owner_phone = State()


class AdminActions(StatesGroup):
    add_admin = State()
