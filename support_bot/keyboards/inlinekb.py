from aiogram.types import  InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData

async def build_inline_kb(arg):
    inline_kb = InlineKeyboardBuilder()
    for key, value in arg.items():
        inline_kb.row(InlineKeyboardButton(text=value, callback_data=key))
    return inline_kb

class Pagination(CallbackData, prefix="page"):
    page: int
    action: str


def paginator(page: int=0):
    builder=InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="⬅️", callback_data=Pagination(page=page, action="prev").pack()),
        InlineKeyboardButton(text="➡️", callback_data=Pagination(page=page, action="next").pack()),
        width = 2
        )
    builder.row(InlineKeyboardButton(text="\U00002B05 Назад к меню", callback_data="back_mmenu", width=1))
    return builder.as_markup()
