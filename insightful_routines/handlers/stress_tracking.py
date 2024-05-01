from datetime import datetime

from aiogram import Bot, F, Router, types
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, ReplyKeyboardMarkup, ReplyKeyboardRemove
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from keyboards.yes_change import get_yes_change_kb
from models import StressLevel, User
from models.models import Session


class StressLevelStatesGroup(StatesGroup):
    choosing_stress_level = State()
    save_data_in_db = State()


def stress_kb() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.button(text="no")
    kb.button(text="low")
    kb.button(text="medium")
    kb.button(text="high")
    kb.adjust(2)
    return kb.as_markup(resize_keyboard=True)


def make_router(bot: Bot) -> Router:
    router = Router()

    @router.message(StateFilter(None), Command("stress"))
    async def start_stress_selection(message: types.Message, state: FSMContext):
        await message.answer(
            "Did you experience stress today?", reply_markup=stress_kb()
        )
        await state.set_state(StressLevelStatesGroup.choosing_stress_level)

    @router.message(StressLevelStatesGroup.choosing_stress_level)
    async def input_stress_level(message: Message, state: FSMContext):
        await state.update_data(chosen_stress_level=message.text.lower())
        await message.answer(
            text=f"You selected: {message.text}. Do you want to save?",
            reply_markup=get_yes_change_kb(),
        )
        await state.set_state(StressLevelStatesGroup.save_data_in_db)

    @router.message(StressLevelStatesGroup.save_data_in_db, F.text.casefold() == "yes")
    async def save_stress_data(message: Message, state: FSMContext):
        await save_data(message, state)

    @router.message(
        StressLevelStatesGroup.save_data_in_db, F.text.casefold() == "change"
    )
    async def change_stress_selection(message: Message, state: FSMContext):
        await state.clear()
        await start_stress_selection(message, state)

    return router


async def save_data(message: Message, state: FSMContext):
    user_data = await state.get_data()

    session = Session()
    try:
        user = session.query(User).filter_by(chat_id=message.from_user.id).first()

        stress_entry = StressLevel(
            user_id=user.id,
            stress=user_data.get("chosen_stress_level"),
            date=datetime.today(),
        )
        session.add(stress_entry)

        session.commit()

        await message.answer(
            "Your data has been saved. Thank you!",
            reply_markup=ReplyKeyboardRemove(),
        )
    except Exception as e:
        session.rollback()
        await message.answer(
            "Sorry, there was an error saving your data. \n You may have already filled out this form today.",
            reply_markup=ReplyKeyboardRemove(),
        )
        print(e)
    finally:
        session.close()
        await state.clear()
