from aiogram.types import ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder


def photo_kb() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.button(text="reverse")
    kb.button(text="preview")
    kb.adjust(2)
    return kb.as_markup(resize_keyboard=True)
