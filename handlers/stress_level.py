from datetime import datetime

from aiogram import F, Router, types
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, ReplyKeyboardRemove

from keyboards.stress import stress_kb
from keyboards.yes_change import get_yes_change_kb
from models import StressLevel, User
from models.models import Session

router = Router()


class StatesStressLevel(StatesGroup):
    choosing_stress_level = State()
    save_data_in_db = State()


@router.message(StateFilter(None), Command("stress"))
async def start_stress_selection(message: types.Message, state: FSMContext):
    await message.answer("Were you stressed today?", reply_markup=stress_kb())
    await state.set_state(StatesStressLevel.choosing_stress_level)


@router.message(StatesStressLevel.choosing_stress_level)
async def input_stress(message: Message, state: FSMContext):
    await state.update_data(chosen_stress_level=message.text.lower())
    await message.answer(
        text=f"You selected: {message.text}. Do you want to save?",
        reply_markup=get_yes_change_kb(),
    )
    await state.set_state(StatesStressLevel.save_data_in_db)


@router.message(StatesStressLevel.save_data_in_db, F.text.casefold() == "yes")
async def process_final_decision(message: Message, state: FSMContext):
    await save_data(message, state)


@router.message(StatesStressLevel.save_data_in_db, F.text.casefold() == "change")
async def process_final_decision2(message: Message, state: FSMContext):
    await state.clear()
    await start_stress_selection(message, state)


async def save_data(message: Message, state: FSMContext):
    user_data = await state.get_data()

    # Assuming your session management is correctly configured
    session = Session()
    try:
        # Check if user already exists
        user = session.query(User).filter_by(chat_id=message.from_user.id).first()
        # Now, save answers
        user_answer = StressLevel(
            user_id=user.id,
            stress=user_data.get("chosen_stress_level"),
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
