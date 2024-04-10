from aiogram.types import ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder


def food_kb() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.button(text="red food")
    kb.button(text="greens")
    kb.button(text="red meat")
    kb.button(text="white meat")
    kb.button(text="fish")
    kb.button(text="seafood")
    kb.button(text="gluten")
    kb.button(text="starch")
    kb.button(text="lactose")
    kb.button(text="other type of sugar")
    kb.button(text="nightshade")
    kb.button(text="white sugar")
    kb.button(text="sweetener")
    kb.button(text="mushrooms")
    kb.button(text="fruits")
    kb.button(text="sweets")
    kb.button(text="eggs")
    kb.button(text="nothing")
    kb.adjust(2)
    return kb.as_markup(resize_keyboard=True)
