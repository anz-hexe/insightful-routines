from datetime import datetime

from aiogram import Bot, F, Router, types
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, ReplyKeyboardMarkup, ReplyKeyboardRemove
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from insightful_routines.keyboards.yes_change import get_yes_change_kb
from insightful_routines.models import LunchIntake, User
from insightful_routines.models.models import Session

SELECTED_LUNCH_PRODUCTS = "selected_lunch_products"


def create_food_keyboard() -> ReplyKeyboardMarkup:
    keyboard_builder = ReplyKeyboardBuilder()
    food_options = [
        "red food",
        "greens",
        "red meat",
        "white meat",
        "fish",
        "seafood",
        "gluten",
        "starch",
        "lactose",
        "other type of sugar",
        "nightshade",
        "white sugar",
        "sweetener",
        "mushrooms",
        "fruits",
        "sweets",
        "eggs",
        "nothing",
    ]
    for option in food_options:
        keyboard_builder.button(text=option)
    keyboard_builder.adjust(2)
    return keyboard_builder.as_markup(resize_keyboard=True)


class LunchStatesGroup(StatesGroup):
    choosing_lunch = State()
    saving_data_in_db = State()


def make_router(bot: Bot) -> Router:
    router = Router()

    @router.message(StateFilter(None), Command("lunch"))
    async def start_lunch_selection(message: types.Message, state: FSMContext):
        await state.set_data({SELECTED_LUNCH_PRODUCTS: []})

        await message.answer(
            "What foods did you eat for lunch today?",
            reply_markup=create_food_keyboard(),
        )
        await state.set_state(LunchStatesGroup.choosing_lunch)

    @router.message(LunchStatesGroup.choosing_lunch)
    async def select_lunch_food(message: types.Message, state: FSMContext):
        data = await state.get_data()
        selected_lunch_products: list = data.get(SELECTED_LUNCH_PRODUCTS)
        valid_options = [
            button.text for row in create_food_keyboard().keyboard for button in row
        ]

        if message.text == "/done":
            await message.answer("Your selected:")
            for product in selected_lunch_products:
                await message.answer(product)
            await message.answer(
                "Do you want to save?", reply_markup=get_yes_change_kb()
            )
            await state.update_data(chosen_lunch=selected_lunch_products)
            await state.set_state(LunchStatesGroup.saving_data_in_db)
        elif message.text in valid_options:
            if message.text not in selected_lunch_products:
                await state.set_data(
                    {
                        SELECTED_LUNCH_PRODUCTS: [
                            message.text,
                            *selected_lunch_products,
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
                reply_markup=create_food_keyboard(),
            )

    @router.message(LunchStatesGroup.saving_data_in_db, F.text.casefold() == "yes")
    async def save_lunch_data(message: Message, state: FSMContext):
        await save_data(message, state)

    @router.message(LunchStatesGroup.saving_data_in_db, F.text.casefold() == "change")
    async def change_lunch_selection(message: Message, state: FSMContext):
        await state.clear()
        await start_lunch_selection(message, state)

    return router


async def save_data(message: Message, state: FSMContext):
    user_data = await state.get_data()

    lunch_products_str = ", ".join(user_data.get("chosen_lunch", []))

    with Session() as session:
        try:
            user = session.query(User).filter_by(chat_id=message.from_user.id).first()
            user_answer = LunchIntake(
                user_id=user.id,
                lunch=lunch_products_str,
                date=datetime.today(),
            )

            print(user_answer)

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
