import os
from datetime import datetime

from aiogram import Bot, F, Router, types
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, ReplyKeyboardRemove

from keyboards.yes_change import get_yes_change_kb
from models import Pimples, User
from models.models import Session


class StatesPimples(StatesGroup):
    choosing_pimples = State()
    save_data_in_db = State()
    add_photo = State()


async def save_data(message: Message, state: FSMContext):
    user_data = await state.get_data()

    # Assuming your session management is correctly configured
    session = Session()
    try:
        # Check if user already exists
        user = session.query(User).filter_by(chat_id=message.from_user.id).first()
        # Now, save answers
        user_answer = Pimples(
            user_id=user.id,
            pimples=user_data.get("chosen_pimples"),
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
    await state.set_state(StatesPimples.add_photo)


def make_router(bot: Bot) -> Router:
    router = Router()

    @router.message(StateFilter(None), Command("pimples"))
    async def start_pimples_selection(message: types.Message, state: FSMContext):
        await message.answer("How many pimples are there today? \n Please enter number")
        await state.set_state(StatesPimples.choosing_pimples)

    @router.message(
        StatesPimples.choosing_pimples, lambda message: message.text.isdigit()
    )
    async def input_pimples(message: Message, state: FSMContext):
        input_pimples = int(message.text)
        await state.update_data(chosen_pimples=input_pimples)
        await message.answer(
            text=f"You selected: {input_pimples}. Do you want to save?",
            reply_markup=get_yes_change_kb(),
        )
        await state.set_state(StatesPimples.save_data_in_db)

    @router.message(
        StatesPimples.choosing_pimples, lambda message: not message.text.isdigit()
    )
    async def handle_not_number(message: types.Message):
        await message.answer("That's not a number! Please send me a number.")

    @router.message(StatesPimples.save_data_in_db, F.text.casefold() == "yes")
    async def process_final_decision(message: Message, state: FSMContext):
        await save_data(message, state)

    @router.message(StatesPimples.save_data_in_db, F.text.casefold() == "change")
    async def process_final_decision2(message: Message, state: FSMContext):
        await state.clear()
        await start_pimples_selection(message, state)

    @router.message(StatesPimples.add_photo, F.photo)
    async def add_photo(message: Message, state: FSMContext):
        await bot.download(
            message.photo[-1],
            destination=f"./data/{message.photo[-1].file_id}.jpg",
        )

    return router
