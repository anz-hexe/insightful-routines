from aiogram.types import ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder


def photo_kb() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.button(text="gallery")
    kb.button(text="make photo")
    kb.adjust(2)
    return kb.as_markup(resize_keyboard=True)
