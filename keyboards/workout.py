from aiogram.types import ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder


def workout_kb() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.button(text="steps")
    kb.button(text="workout in gym")
    kb.button(text="workout in outside")
    kb.button(text="massage")
    kb.button(text="pool")
    # TODO
    # kb.button(text="other")
    kb.adjust(2)
    return kb.as_markup(resize_keyboard=True)
