from aiogram.types import ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder


def skincare_kb() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.button(text="cleaner")
    kb.button(text="tonic")
    kb.button(text="serum")
    kb.button(text="eye cream")
    kb.button(text="cream")
    kb.button(text="patch")
    kb.button(text="eye patchs")
    kb.button(text="sunscreen")
    kb.button(text="pilling")
    kb.button(text="scrub")
    kb.button(text="spot cream")
    kb.button(text="mask")
    kb.button(text="skin picking(")
    kb.button(text="nothing")
    # TODO
    # kb.button(text="done")
    kb.adjust(2)
    return kb.as_markup(resize_keyboard=True)
