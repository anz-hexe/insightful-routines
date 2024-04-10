from aiogram.types import ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder


def drinks_hot_kb() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.button(text="green tea")
    kb.button(text="black tea")
    kb.button(text="coffee")
    kb.button(text="herbal tea")
    kb.button(text="other")
    kb.button(text="no")
    # TODO
    # kb.button(text="other, please enter")
    kb.adjust(2)
    return kb.as_markup(resize_keyboard=True)
