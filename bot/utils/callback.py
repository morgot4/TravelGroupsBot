from aiogram.filters.callback_data import CallbackData


class MarkDetails(CallbackData, prefix="details"):
    id: int
    mark_code: str
