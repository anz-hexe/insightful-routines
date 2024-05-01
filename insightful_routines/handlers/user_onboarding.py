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

from insightful_routines.models import User, UserAnswer
from insightful_routines.models.models import Session

CHOICES_AGE_GROUP = ["up to 25", "25 - 30", "30 - 45", "45+"]
CHOICES_ALLERGIES = ["yes", "no", "not that i'm aware of"]
CHOICES_MEDICATIONS = ["yes", "no"]
CHOICES_SKIN_TYPE = ["normal", "dry", "oily", "combination", "sensitive"]
CHOICES_DATA_MANAGEMENT = ["yes", "change"]


def create_reply_keyboard(options: list[str]) -> ReplyKeyboardMarkup:
    buttons = [KeyboardButton(text=option) for option in options]
    return ReplyKeyboardMarkup(keyboard=[buttons], resize_keyboard=True)


USERS_CURRENT_QUESTION = {}


class FirstMeetStateGroup(StatesGroup):
    choosing_age = State()
    choosing_allergies = State()
    choosing_medicines = State()
    choosing_skin_type = State()
    saving_data_in_db = State()


def make_router(bot: Bot) -> Router:
    router = Router()

    @router.message(StateFilter(None), Command("first_meeting"))
    async def start_first_meeting(message: Message, state: FSMContext):
        await message.answer(
            text="How old are you?",
            reply_markup=create_reply_keyboard(CHOICES_AGE_GROUP),
        )
        await state.set_state(FirstMeetStateGroup.choosing_age)

    @router.message(FirstMeetStateGroup.choosing_age, F.text.in_(CHOICES_AGE_GROUP))
    async def input_age_group(message: Message, state: FSMContext):
        await state.update_data(chosen_age_group=message.text.lower())
        await message.answer(
            text="Do you have any allergies?",
            reply_markup=create_reply_keyboard(CHOICES_ALLERGIES),
        )
        await state.set_state(FirstMeetStateGroup.choosing_allergies)

    @router.message(
        FirstMeetStateGroup.choosing_allergies, F.text.in_(CHOICES_ALLERGIES)
    )
    async def input_allergies(message: Message, state: FSMContext):
        await state.update_data(chosen_allergies=message.text.lower())
        await message.answer(
            text="Do you take any medications on a regular basis?",
            reply_markup=create_reply_keyboard(CHOICES_MEDICATIONS),
        )
        await state.set_state(FirstMeetStateGroup.choosing_medicines)

    @router.message(
        FirstMeetStateGroup.choosing_medicines, F.text.in_(CHOICES_MEDICATIONS)
    )
    async def input_medications(message: Message, state: FSMContext):
        await state.update_data(chosen_medications=message.text.lower())
        await message.answer(
            text="What skin type do you have?",
            reply_markup=create_reply_keyboard(CHOICES_SKIN_TYPE),
        )
        await state.set_state(FirstMeetStateGroup.choosing_skin_type)

    @router.message(
        FirstMeetStateGroup.choosing_skin_type, F.text.in_(CHOICES_SKIN_TYPE)
    )
    async def input_skin_type(message: Message, state: FSMContext):
        await state.update_data(chosen_skin_type=message.text.lower())
        user_data = await state.get_data()
        await message.answer(
            text=f"Your answers: \n Age: {user_data.get('chosen_age_group')} \n Allergies: {user_data.get('chosen_allergies')} \n Medications: {user_data.get('chosen_medications')} \n Skin type: {user_data.get('chosen_skin_type')}",
            reply_markup=create_reply_keyboard(CHOICES_DATA_MANAGEMENT),
        )
        await state.set_state(FirstMeetStateGroup.saving_data_in_db)

    @router.message(FirstMeetStateGroup.saving_data_in_db, F.text.casefold() == "yes")
    async def save_user_data(message: Message, state: FSMContext):
        await save_user_answers(message, state)

    @router.message(
        FirstMeetStateGroup.saving_data_in_db, F.text.casefold() == "change"
    )
    async def change_user_data(message: Message, state: FSMContext):
        await state.clear()
        await start_first_meeting(message, state)

    return router


async def save_user_answers(message: Message, state: FSMContext):
    user_data = await state.get_data()

    session = Session()
    try:
        user = session.query(User).filter_by(chat_id=message.from_user.id).first()

        user_answer = UserAnswer(
            user_id=user.id,
            question_old=user_data.get("chosen_age_group"),
            question_allergen=user_data.get("chosen_allergies"),
            question_medicines=user_data.get("chosen_medications"),
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
