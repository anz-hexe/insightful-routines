from datetime import datetime

from aiogram import Bot, F, Router, types
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, ReplyKeyboardRemove

from keyboards.yes_change import get_yes_change_kb
from keyboards.yes_no import get_yes_no_kb
from models import User, WaterIntake
from models.models import Session


class WaterIntakeStatesGroup(StatesGroup):
    choosing_water_intake = State()
    saving_data_in_db = State()


def make_router(bot: Bot) -> Router:
    router = Router()

    @router.message(StateFilter(None), Command("drink_water"))
    async def start_water_intake_selection(message: types.Message, state: FSMContext):
        await message.answer(
            "Did you drink your daily amount of water today?",
            reply_markup=get_yes_no_kb(),
        )
        await state.set_state(WaterIntakeStatesGroup.choosing_water_intake)

    @router.message(WaterIntakeStatesGroup.choosing_water_intake)
    async def input_water_intake(message: Message, state: FSMContext):
        chosen_water_intake = message.text.lower()
        await state.update_data(chosen_water_intake=chosen_water_intake)
        await message.answer(
            text=f"You selected: {message.text}. Do you want to save?",
            reply_markup=get_yes_change_kb(),
        )
        await state.set_state(WaterIntakeStatesGroup.saving_data_in_db)

    @router.message(
        WaterIntakeStatesGroup.saving_data_in_db, F.text.casefold() == "yes"
    )
    async def save_water_intake_data(message: Message, state: FSMContext):
        await save_data(message, state)

    @router.message(
        WaterIntakeStatesGroup.saving_data_in_db, F.text.casefold() == "change"
    )
    async def change_water_intake_selection(message: Message, state: FSMContext):
        await state.clear()
        await start_water_intake_selection(message, state)

    return router


async def save_data(message: Message, state: FSMContext):
    user_data = await state.get_data()

    session = Session()
    try:
        user = session.query(User).filter_by(chat_id=message.from_user.id).first()

        water_intake_entry = WaterIntake(
            user_id=user.id,
            water=user_data.get("chosen_water_intake"),
            date=datetime.today(),
        )
        session.add(water_intake_entry)

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
