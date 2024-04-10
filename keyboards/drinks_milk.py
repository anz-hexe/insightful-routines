from aiogram.types import ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder


def milk_kb() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.button(text="yes, cow")
    kb.button(text="yes, lactose free")
    kb.button(text="yes, alternative")
    kb.button(text="no")
    kb.adjust(2)
    return kb.as_markup(resize_keyboard=True)
