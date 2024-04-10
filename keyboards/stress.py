from aiogram.types import ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder


def stress_kb() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.button(text="no")
    kb.button(text="low")
    kb.button(text="medium")
    kb.button(text="high")
    kb.adjust(2)
    return kb.as_markup(resize_keyboard=True)
