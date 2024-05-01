from datetime import datetime

from aiogram import Bot, F, Router, types
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, ReplyKeyboardRemove

from insightful_routines.keyboards.yes_change import get_yes_change_kb
from insightful_routines.keyboards.yes_no import get_yes_no_kb
from insightful_routines.models import Supplements, User
from insightful_routines.models.models import Session


class SupplementsStatesGroup(StatesGroup):
    choosing_supplements = State()
    saving_data_in_db = State()


def make_router(bot: Bot) -> Router:
    router = Router()

    @router.message(StateFilter(None), Command("supplements"))
    async def start_supplements_selection(message: types.Message, state: FSMContext):
        await message.answer(
            "Did you take any supplements?", reply_markup=get_yes_no_kb()
        )
        await state.set_state(SupplementsStatesGroup.choosing_supplements)

    @router.message(SupplementsStatesGroup.choosing_supplements)
    async def input_supplements(message: Message, state: FSMContext):
        chosen_supplements = message.text.lower()
        await state.update_data(chosen_supplements=chosen_supplements)
        await message.answer(
            text=f"You selected: {message.text}. Do you want to save?",
            reply_markup=get_yes_change_kb(),
        )
        await state.set_state(SupplementsStatesGroup.saving_data_in_db)

    @router.message(
        SupplementsStatesGroup.saving_data_in_db, F.text.casefold() == "yes"
    )
    async def save_supplements_data(message: Message, state: FSMContext):
        await save_data(message, state)

    @router.message(
        SupplementsStatesGroup.saving_data_in_db, F.text.casefold() == "change"
    )
    async def change_supplements_selection(message: Message, state: FSMContext):
        await state.clear()
        await start_supplements_selection(message, state)

    return router


async def save_data(message: Message, state: FSMContext):
    user_data = await state.get_data()

    session = Session()
    try:
        user = session.query(User).filter_by(chat_id=message.from_user.id).first()

        supplements_entry = Supplements(
            user_id=user.id,
            supplements=user_data.get("chosen_supplements"),
            date=datetime.today(),
        )
        session.add(supplements_entry)

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
