from datetime import datetime

from aiogram import Bot, F, Router, types
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, ReplyKeyboardRemove

from keyboards.drinks_hot import drinks_hot_kb
from keyboards.yes_change import get_yes_change_kb
from models import HotDrinksIntake, User
from models.models import Session

SELECTED_DRINKS_HOT = "selected_drinks_hot"


class StatesDrinksHot(StatesGroup):
    choosing_drinks_hot = State()
    save_data_in_db = State()


def make_router(bot: Bot) -> Router:
    router = Router()

    @router.message(StateFilter(None), Command("hot_drinks"))
    async def start_drinks_hot_selection(message: types.Message, state: FSMContext):
        await state.set_data({SELECTED_DRINKS_HOT: []})

        await message.answer(
            "What hot drinks did you drink today?", reply_markup=drinks_hot_kb()
        )
        await state.set_state(StatesDrinksHot.choosing_drinks_hot)

    @router.message(StatesDrinksHot.choosing_drinks_hot)
    async def select_drinks_hot(message: types.Message, state: FSMContext):
        data = await state.get_data()
        selected_products_drinks_hot: list = data.get(SELECTED_DRINKS_HOT)
        valid_button_texts = []
        for row in drinks_hot_kb().keyboard:
            for button in row:
                valid_button_texts.append(button.text)

        if message.text == "/done":
            await message.answer("Your selected:")
            for product in selected_products_drinks_hot:
                await message.answer(product)
            await message.answer(
                "Do you want to save?", reply_markup=get_yes_change_kb()
            )
            await state.update_data(chosen_drinks_hot=selected_products_drinks_hot)
            await state.set_state(StatesDrinksHot.save_data_in_db)
        elif message.text in valid_button_texts:
            if message.text not in selected_products_drinks_hot:
                await state.set_data(
                    {
                        SELECTED_DRINKS_HOT: [
                            message.text,
                            *selected_products_drinks_hot,
                        ]
                    }
                )
                await message.answer(
                    f"You selected: {message.text}. Select more or click   /done   when finished."
                )
            else:
                await message.answer(
                    "You've already selected this product. Select another or click   /done when   finished."
                )
        else:
            await message.answer(
                "Please select from the list or click   /done   when finished.",
                reply_markup=drinks_hot_kb(),
            )

    @router.message(StatesDrinksHot.save_data_in_db, F.text.casefold() == "yes")
    async def process_final_decision_yes(message: Message, state: FSMContext):
        await save_data(message, state)

    @router.message(StatesDrinksHot.save_data_in_db, F.text.casefold() == "change")
    async def process_final_decision_change(message: Message, state: FSMContext):
        await state.clear()
        await start_drinks_hot_selection(message, state)

    return router


async def save_data(message: Message, state: FSMContext):
    user_data = await state.get_data()

    drinks_hot_str = ", ".join(user_data.get("chosen_drinks_hot", []))

    with Session() as session:
        try:
            # session.begin()
            user = session.query(User).filter_by(chat_id=message.from_user.id).first()
            user_answer = HotDrinksIntake(
                user_id=user.id,
                hot_drinks=drinks_hot_str,
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
