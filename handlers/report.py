import pandas as pd
from aiogram import Bot, Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, ReplyKeyboardRemove

from keyboards.yes_no import get_yes_no_kb
from models import (
    BreakfastIntake,
    DinnerIntake,
    EveningSkincare,
    FacePhoto,
    HotDrinksIntake,
    LunchIntake,
    MilkDrinksIntake,
    MorningSkincare,
    OtherDrinksIntake,
    Pimples,
    SnacksIntake,
    StressLevel,
    Supplements,
    User,
    UserAnswer,
    WaterIntake,
    Workouts,
)
from models.models import Session


class StatesReport(StatesGroup):
    reporting = State()
    save_data_in_db = State()


def make_router(bot: Bot) -> Router:
    router = Router()

    @router.message(StateFilter(None), Command("report"))
    async def start_reporting(message: Message, state: FSMContext):
        await message.answer(
            "Do you want to receive a report?", reply_markup=get_yes_no_kb()
        )
        await state.set_state(StatesReport.reporting)

    @router.message(StatesReport.reporting)
    async def get_data(message: Message, state: FSMContext):
        session = Session()

        query = (
            session.query(
                BreakfastIntake,
                DinnerIntake,
                EveningSkincare,
                FacePhoto,
                HotDrinksIntake,
                LunchIntake,
                MilkDrinksIntake,
                MorningSkincare,
                OtherDrinksIntake,
                Pimples,
                SnacksIntake,
                StressLevel,
                Supplements,
                User,
                UserAnswer,
                WaterIntake,
                Workouts,
            )
            .outerjoin(User.answers)
            .outerjoin(User.breakfast)
            .outerjoin(User.dinner)
            .outerjoin(User.evening_skincare)
            .outerjoin(User.face_photo)
            .outerjoin(User.hot_drinks)
            .outerjoin(User.lunch)
            .outerjoin(User.milk_drinks)
            .outerjoin(User.morning_skincare)
            .outerjoin(User.other_drinks)
            .outerjoin(User.pimples)
            .outerjoin(User.snacks)
            .outerjoin(User.stress_level)
            .outerjoin(User.supplements)
            .outerjoin(User.water)
            .outerjoin(User.workouts)
            .filter(User.chat_id == message.from_user.id)
        )

        with session.connection() as conn:
            print(pd.read_sql(query.statement, conn))
            data = pd.read_sql(query.statement, conn)
            data.to_csv(f"data/report_user_{message.from_user.id}.csv", index=False)

    return router
