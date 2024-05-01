from datetime import datetime

from aiogram import Bot, F, Router, types
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, ReplyKeyboardMarkup, ReplyKeyboardRemove
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from insightful_routines.keyboards.yes_change import get_yes_change_kb
from insightful_routines.models import BreakfastIntake, User
from insightful_routines.models.models import Session

SELECTED_BREAKFAST_PRODUCTS = "selected_breakfast_products"


class BreakfastStatesGroup(StatesGroup):
    choosing_breakfast = State()
    saving_data_in_db = State()


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


def make_router(bot: Bot) -> Router:
    router = Router()

    @router.message(StateFilter(None), Command("breakfast"))
    async def start_breakfast_selection(message: types.Message, state: FSMContext):
        await state.set_data({SELECTED_BREAKFAST_PRODUCTS: []})

        await message.answer(
            "What foods did you eat for breakfast today?",
            reply_markup=create_food_keyboard(),
        )
        await state.set_state(BreakfastStatesGroup.choosing_breakfast)

    @router.message(BreakfastStatesGroup.choosing_breakfast)
    async def select_breakfast_food(message: types.Message, state: FSMContext):
        data = await state.get_data()
        selected_breakfast_products: list = data.get(SELECTED_BREAKFAST_PRODUCTS)
        valid_options = [
            button.text for row in create_food_keyboard().keyboard for button in row
        ]

        if message.text == "/done":
            await message.answer("Your selected foods for breakfast:")
            for product in selected_breakfast_products:
                await message.answer(product)
            await message.answer(
                "Do you want to save?", reply_markup=get_yes_change_kb()
            )
            await state.update_data(chosen_breakfast=selected_breakfast_products)
            await state.set_state(BreakfastStatesGroup.saving_data_in_db)
        elif message.text in valid_options:
            if message.text not in selected_breakfast_products:
                await state.set_data(
                    {
                        SELECTED_BREAKFAST_PRODUCTS: [
                            message.text,
                            *selected_breakfast_products,
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

    @router.message(BreakfastStatesGroup.saving_data_in_db, F.text.casefold() == "yes")
    async def save_breakfast_data(message: Message, state: FSMContext):
        await save_data(message, state)

    @router.message(
        BreakfastStatesGroup.saving_data_in_db, F.text.casefold() == "change"
    )
    async def change_breakfast_selection(message: Message, state: FSMContext):
        await state.clear()
        await start_breakfast_selection(message, state)

    return router


async def save_data(message: Message, state: FSMContext):
    user_data = await state.get_data()

    breakfast_products_str = ", ".join(user_data.get("chosen_breakfast", []))

    with Session() as session:
        try:
            user = session.query(User).filter_by(chat_id=message.from_user.id).first()
            user_answer = BreakfastIntake(
                user_id=user.id,
                breakfast=breakfast_products_str,
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
