from aiogram.types import ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder


def other_drinks_kb() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.button(text="alcohol")
    kb.button(text="energy drink")
    kb.button(text="juice")
    kb.button(text="soft drink")
    kb.button(text="sparkling mineral water")
    kb.button(text="no")
    # TODO
    # kb.button(text="other")
    kb.adjust(2)
    return kb.as_markup(resize_keyboard=True)
