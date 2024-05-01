from datetime import datetime

from aiogram import Bot, F, Router, types
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, ReplyKeyboardMarkup, ReplyKeyboardRemove
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from insightful_routines.keyboards.yes_change import get_yes_change_kb
from insightful_routines.models import User, Workouts
from insightful_routines.models.models import Session


class WorkoutsStatesGroup(StatesGroup):
    choosing_workouts = State()
    saving_data_in_db = State()


def create_workouts_keyboard() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.button(text="no")
    kb.button(text="steps")
    kb.button(text="workout in gym")
    kb.button(text="workout in outside")
    kb.button(text="massage")
    kb.button(text="pool")
    # TODO
    # kb.button(text="other")
    kb.adjust(2)
    return kb.as_markup(resize_keyboard=True)


def make_router(bot: Bot) -> Router:
    router = Router()

    @router.message(StateFilter(None), Command("workouts"))
    async def start_workouts_selection(message: types.Message, state: FSMContext):
        await message.answer(
            "Did you do any workouts today?", reply_markup=create_workouts_keyboard()
        )
        await state.set_state(WorkoutsStatesGroup.choosing_workouts)

    @router.message(WorkoutsStatesGroup.choosing_workouts)
    async def input_workouts(message: Message, state: FSMContext):
        chosen_workouts = message.text.lower()
        await state.update_data(chosen_workouts=chosen_workouts)
        await message.answer(
            text=f"You selected: {message.text}. Do you want to save?",
            reply_markup=get_yes_change_kb(),
        )
        await state.set_state(WorkoutsStatesGroup.saving_data_in_db)

    @router.message(WorkoutsStatesGroup.saving_data_in_db, F.text.casefold() == "yes")
    async def save_workouts_data(message: Message, state: FSMContext):
        await save_data(message, state)

    @router.message(
        WorkoutsStatesGroup.saving_data_in_db, F.text.casefold() == "change"
    )
    async def change_workouts_selection(message: Message, state: FSMContext):
        await state.clear()
        await start_workouts_selection(message, state)

    return router


async def save_data(message: Message, state: FSMContext):
    user_data = await state.get_data()

    session = Session()
    try:
        user = session.query(User).filter_by(chat_id=message.from_user.id).first()

        workouts_entry = Workouts(
            user_id=user.id,
            workouts=user_data.get("chosen_workouts"),
            date=datetime.today(),
        )
        session.add(workouts_entry)

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
