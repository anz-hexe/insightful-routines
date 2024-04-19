from datetime import datetime

from aiogram import Bot, F, Router, types
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, ReplyKeyboardRemove

from keyboards.food import food_kb
from keyboards.yes_change import get_yes_change_kb
from models import BreakfastIntake, User
from models.models import Session

SELECTED_PRODUCTS_BREAKFAST = "selected_breakfast"


class StatesBreakfast(StatesGroup):
    choosing_breakfast = State()
    save_data_in_db = State()


def make_router(bot: Bot) -> Router:
    router = Router()

    @router.message(StateFilter(None), Command("breakfast"))
    async def start_breakfast_selection(message: types.Message, state: FSMContext):
        await state.set_data({SELECTED_PRODUCTS_BREAKFAST: []})

        await message.answer(
            "What foods did you eat for breakfast today?", reply_markup=food_kb()
        )
        await state.set_state(StatesBreakfast.choosing_breakfast)

    @router.message(StatesBreakfast.choosing_breakfast)
    async def select_breakfast_product(message: types.Message, state: FSMContext):
        data = await state.get_data()
        selected_products_breakfast: list = data.get(SELECTED_PRODUCTS_BREAKFAST)
        valid_button_texts = []
        for row in food_kb().keyboard:
            for button in row:
                valid_button_texts.append(button.text)

        if message.text == "/done":
            await message.answer("Your selected:")
            for product in selected_products_breakfast:
                await message.answer(product)
            await message.answer(
                "Do you want to save?", reply_markup=get_yes_change_kb()
            )
            await state.update_data(chosen_breakfast=selected_products_breakfast)
            await state.set_state(StatesBreakfast.save_data_in_db)
        elif message.text in valid_button_texts:
            if message.text not in selected_products_breakfast:
                await state.set_data(
                    {
                        SELECTED_PRODUCTS_BREAKFAST: [
                            message.text,
                            *selected_products_breakfast,
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
                reply_markup=food_kb(),
            )

    @router.message(StatesBreakfast.save_data_in_db, F.text.casefold() == "yes")
    async def process_final_decision_yes(message: Message, state: FSMContext):
        await save_data(message, state)

    @router.message(StatesBreakfast.save_data_in_db, F.text.casefold() == "change")
    async def process_final_decision_change(message: Message, state: FSMContext):
        await state.clear()
        await start_breakfast_selection(message, state)

    return router


async def save_data(message: Message, state: FSMContext):
    user_data = await state.get_data()

    breakfast_products_str = ", ".join(user_data.get("chosen_breakfast", []))

    with Session() as session:
        try:
            # session.begin()
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
            print(e)  # Log the error for debugging
        finally:
            await state.clear()
