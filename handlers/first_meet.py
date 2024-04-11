from aiogram import Bot, F, Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    KeyboardButton,
    Message,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)

from models import User, UserAnswer
from models.models import Session


def make_row_keyboard(items: list[str]) -> ReplyKeyboardMarkup:
    row = [KeyboardButton(text=item) for item in items]
    return ReplyKeyboardMarkup(keyboard=[row], resize_keyboard=True)


choices_old = ["up to 25", "25 - 30", "30 - 45", "45+"]
choices_allergies = ["yes", "no", "not that i'm aware of"]
choices_medicines = ["yes", "no"]
choices_skin_type = ["normal", "dry", "oily", "combination", "sensitive"]
data_in_db = ["yes", "change"]

USERS_CURRENT_QUESTION = {}


class FirstMeet(StatesGroup):
    choosing_old = State()
    choosing_allergies = State()
    choosing_medicines = State()
    choosing_skin_type = State()
    save_data_in_db = State()


def make_router(bot: Bot) -> Router:
    router = Router()

    @router.message(StateFilter(None), Command("first_meeting"))
    async def input_data(message: Message, state: FSMContext):
        await message.answer(
            text="How old are you?", reply_markup=make_row_keyboard(choices_old)
        )
        await state.set_state(FirstMeet.choosing_old)

    @router.message(FirstMeet.choosing_old, F.text.in_(choices_old))
    async def input_old(message: Message, state: FSMContext):
        await state.update_data(chosen_old=message.text.lower())
        await message.answer(
            text="Do you have any allergies?",
            reply_markup=make_row_keyboard(choices_allergies),
        )
        await state.set_state(FirstMeet.choosing_allergies)

    @router.message(FirstMeet.choosing_allergies, F.text.in_(choices_allergies))
    async def input_allergies(message: Message, state: FSMContext):
        await state.update_data(chosen_allergies=message.text.lower())
        await message.answer(
            text="Do you take any medications on a regular basis?",
            reply_markup=make_row_keyboard(choices_medicines),
        )
        await state.set_state(FirstMeet.choosing_medicines)

    @router.message(FirstMeet.choosing_medicines, F.text.in_(choices_medicines))
    async def input_medicines(message: Message, state: FSMContext):
        await state.update_data(chosen_medicines=message.text.lower())
        await message.answer(
            text="What skin type do you have?",
            reply_markup=make_row_keyboard(choices_skin_type),
        )
        await state.set_state(FirstMeet.choosing_skin_type)

    @router.message(FirstMeet.choosing_skin_type, F.text.in_(choices_skin_type))
    async def input_skin_type(message: Message, state: FSMContext):
        await state.update_data(chosen_skin_type=message.text.lower())
        user_data = await state.get_data()
        await message.answer(
            text=f"Your answers: \n Age: {user_data.get('chosen_old')} \n Allergies: {user_data.get('chosen_allergies')} \n Medicines: {user_data.get('chosen_medicines')} \n Skin type: {user_data.get('chosen_skin_type')}",
            reply_markup=make_row_keyboard(data_in_db),
        )
        await state.set_state(FirstMeet.save_data_in_db)

    @router.message(FirstMeet.save_data_in_db, F.text.casefold() == "yes")
    async def process_final_decision(message: Message, state: FSMContext):
        await save_data(message, state)

    @router.message(FirstMeet.save_data_in_db, F.text.casefold() == "change")
    async def process_final_decision2(message: Message, state: FSMContext):
        await state.clear()
        await input_data(message, state)

    return router


async def save_data(message: Message, state: FSMContext):
    user_data = await state.get_data()

    # Assuming your session management is correctly configured
    session = Session()
    try:
        # Check if user already exists
        user = session.query(User).filter_by(chat_id=message.from_user.id).first()
        # Now, save answers
        user_answer = UserAnswer(
            user_id=user.id,
            question_old=user_data.get("chosen_old"),
            question_allergen=user_data.get("chosen_allergies"),
            question_medicines=user_data.get("chosen_medicines"),
            question_skin_type=user_data.get("chosen_skin_type"),
        )
        session.add(user_answer)

        session.commit()

        await message.answer(
            "Your data has been saved. Thank you! \n Please use the menu to fill out forms.",
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
