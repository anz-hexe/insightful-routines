from datetime import datetime

from aiogram import Bot, F, Router, types
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, ReplyKeyboardMarkup, ReplyKeyboardRemove
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from insightful_routines.keyboards.yes_change import get_yes_change_kb
from insightful_routines.models import MorningSkincare, User
from insightful_routines.models.models import Session

SELECTED_MORNING_SKINCARE_PRODUCTS = "selected_morning_skincare_products"


class MorningSkincareStatesGroup(StatesGroup):
    choosing_skincare = State()
    saving_data_in_db = State()


def create_morning_skincare_keyboard() -> ReplyKeyboardMarkup:
    keyboard_builder = ReplyKeyboardBuilder()
    skincare_options = [
        "cleanser",
        "toner",
        "serum",
        "eye cream",
        "cream",
        "patch",
        "eye patches",
        "sunscreen",
        "peeling",
        "scrub",
        "spot treatment",
        "mask",
        "skin picking",
        "none",
    ]
    for option in skincare_options:
        keyboard_builder.button(text=option)
    keyboard_builder.adjust(2)
    return keyboard_builder.as_markup(resize_keyboard=True)


def make_router(bot: Bot) -> Router:
    router = Router()

    @router.message(StateFilter(None), Command("mornig_skincare"))
    async def start_morning_skincare_selection(
        message: types.Message, state: FSMContext
    ):
        await state.set_data({SELECTED_MORNING_SKINCARE_PRODUCTS: []})

        await message.answer(
            "What skin products did you use this morning?",
            reply_markup=create_morning_skincare_keyboard(),
        )
        await state.set_state(MorningSkincareStatesGroup.choosing_skincare)

    @router.message(MorningSkincareStatesGroup.choosing_skincare)
    async def select_morning_skincare(message: types.Message, state: FSMContext):
        data = await state.get_data()
        selected_products: list = data.get(SELECTED_MORNING_SKINCARE_PRODUCTS)
        valid_options = [
            button.text
            for row in create_morning_skincare_keyboard().keyboard
            for button in row
        ]

        if message.text == "/done":
            await message.answer("Your selected skincare products are:")
            for product in selected_products:
                await message.answer(product)
            await message.answer(
                "Do you want to save?", reply_markup=get_yes_change_kb()
            )
            await state.update_data(chosen_skincare=selected_products)
            await state.set_state(MorningSkincareStatesGroup.saving_data_in_db)
        elif message.text in valid_options:
            if message.text not in selected_products:
                await state.set_data(
                    {
                        SELECTED_MORNING_SKINCARE_PRODUCTS: [
                            message.text,
                            *selected_products,
                        ]
                    }
                )
                await message.answer(
                    f"You selected: {message.text}. Select more or click   /done   when finished."
                )
            else:
                await message.answer(
                    "You've already selected this product. Select another or click   /done   when finished."
                )
        else:
            await message.answer(
                "Please select from the list or click   /done   when finished.",
                reply_markup=create_morning_skincare_keyboard(),
            )

    @router.message(
        MorningSkincareStatesGroup.saving_data_in_db, F.text.casefold() == "yes"
    )
    async def save_morning_skincare_data(message: Message, state: FSMContext):
        await save_data(message, state)

    @router.message(
        MorningSkincareStatesGroup.saving_data_in_db, F.text.casefold() == "change"
    )
    async def change_morning_skincare_selection(message: Message, state: FSMContext):
        await state.clear()
        await start_morning_skincare_selection(message, state)

    return router


async def save_data(message: Message, state: FSMContext):
    user_data = await state.get_data()

    morning_skincare_products_str = ", ".join(user_data.get("chosen_skincare", []))

    with Session() as session:
        try:
            user = session.query(User).filter_by(chat_id=message.from_user.id).first()
            user_answer = MorningSkincare(
                user_id=user.id,
                morning_skincare=morning_skincare_products_str,
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
            print(e)
        finally:
            await state.clear()
