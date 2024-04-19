from datetime import datetime

from aiogram import Bot, F, Router, types
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, ReplyKeyboardRemove

from keyboards.yes_change import get_yes_change_kb
from keyboards.yes_no import get_yes_no_kb
from models import SnacksIntake, User
from models.models import Session


class StatesSnacks(StatesGroup):
    choosing_snacks = State()
    save_data_in_db = State()


def make_router(bot: Bot) -> Router:
    router = Router()

    @router.message(StateFilter(None), Command("snacks"))
    async def start_snacks_selection(message: types.Message, state: FSMContext):
        await message.answer(
            "Did you have any snacks today?", reply_markup=get_yes_no_kb()
        )
        await state.set_state(StatesSnacks.choosing_snacks)

    @router.message(StatesSnacks.choosing_snacks)
    async def input_snacks(message: Message, state: FSMContext):
        await state.update_data(chosen_snacks=message.text.lower())
        await message.answer(
            text=f"You selected: {message.text}. Do you want to save?",
            reply_markup=get_yes_change_kb(),
        )
        await state.set_state(StatesSnacks.save_data_in_db)

    @router.message(StatesSnacks.save_data_in_db, F.text.casefold() == "yes")
    async def process_final_decision(message: Message, state: FSMContext):
        await save_data(message, state)

    @router.message(StatesSnacks.save_data_in_db, F.text.casefold() == "change")
    async def process_final_decision2(message: Message, state: FSMContext):
        await state.clear()
        await start_snacks_selection(message, state)

    return router


async def save_data(message: Message, state: FSMContext):
    user_data = await state.get_data()

    # Assuming your session management is correctly configured
    session = Session()
    try:
        # Check if user already exists
        user = session.query(User).filter_by(chat_id=message.from_user.id).first()
        # Now, save answers
        user_answer = SnacksIntake(
            user_id=user.id,
            snacks=user_data.get("chosen_snacks"),
            date=datetime.today(),
        )
        session.add(user_answer)

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
        print(e)  # Log the error for debugging
    finally:
        session.close()
        await state.clear()
