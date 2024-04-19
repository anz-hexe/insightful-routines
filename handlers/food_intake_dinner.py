from datetime import datetime

from aiogram import Bot, F, Router, types
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, ReplyKeyboardRemove

from keyboards.food import food_kb
from keyboards.yes_change import get_yes_change_kb
from models import DinnerIntake, User
from models.models import Session

SELECTED_PRODUCTS_DINNER = "selected_dinner"


class StatesDinner(StatesGroup):
    choosing_dinner = State()
    save_data_in_db = State()


def make_router(bot: Bot) -> Router:
    router = Router()

    @router.message(StateFilter(None), Command("dinner"))
    async def start_dinner_selection(message: types.Message, state: FSMContext):
        await state.set_data({SELECTED_PRODUCTS_DINNER: []})

        await message.answer(
            "What foods did you eat for dinner today?", reply_markup=food_kb()
        )
        await state.set_state(StatesDinner.choosing_dinner)

    @router.message(StatesDinner.choosing_dinner)
    async def select_dinner_product(message: types.Message, state: FSMContext):
        data = await state.get_data()
        selected_products_dinner: list = data.get(SELECTED_PRODUCTS_DINNER)
        valid_button_texts = []
        for row in food_kb().keyboard:
            for button in row:
                valid_button_texts.append(button.text)

        if message.text == "/done":
            await message.answer("Your selected:")
            for product in selected_products_dinner:
                await message.answer(product)
            await message.answer(
                "Do you want to save?", reply_markup=get_yes_change_kb()
            )
            await state.update_data(chosen_dinner=selected_products_dinner)
            await state.set_state(StatesDinner.save_data_in_db)
        elif message.text in valid_button_texts:
            if message.text not in selected_products_dinner:
                await state.set_data(
                    {
                        SELECTED_PRODUCTS_DINNER: [
                            message.text,
                            *selected_products_dinner,
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

    @router.message(StatesDinner.save_data_in_db, F.text.casefold() == "yes")
    async def process_final_decision_yes(message: Message, state: FSMContext):
        await save_data(message, state)

    @router.message(StatesDinner.save_data_in_db, F.text.casefold() == "change")
    async def process_final_decision_change(message: Message, state: FSMContext):
        await state.clear()
        await start_dinner_selection(message, state)

    return router


async def save_data(message: Message, state: FSMContext):
    user_data = await state.get_data()

    dinner_products_str = ", ".join(user_data.get("chosen_dinner", []))

    with Session() as session:
        try:
            # session.begin()
            user = session.query(User).filter_by(chat_id=message.from_user.id).first()
            user_answer = DinnerIntake(
                user_id=user.id,
                dinner=dinner_products_str,
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
