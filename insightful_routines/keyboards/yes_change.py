from aiogram.types import ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder


def get_yes_change_kb() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.button(text="yes")
    kb.button(text="change")
    kb.adjust(2)
    return kb.as_markup(resize_keyboard=True)
