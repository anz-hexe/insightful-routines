from datetime import datetime

from aiogram import Bot, F, Router, types
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, ReplyKeyboardRemove

from keyboards.skincare import skincare_kb
from keyboards.yes_change import get_yes_change_kb
from models import AppliedAt, SkincareCosmetics, User
from models.models import Session

SELECTED_PRODUCTS = "selected_products"


class StatesMorningSkincare(StatesGroup):
    choosing_skincare = State()
    save_data_in_db = State()


def make_router(bot: Bot) -> Router:
    router = Router()

    @router.message(StateFilter(None), Command("mornig_skincare"))
    async def start_skincare_selection(message: types.Message, state: FSMContext):
        print(f"{__file__}")
        await state.set_data({SELECTED_PRODUCTS: []})

        await message.answer(
            "What skin products did you use this morning?", reply_markup=skincare_kb()
        )
        await state.set_state(StatesMorningSkincare.choosing_skincare)

    @router.message(StatesMorningSkincare.choosing_skincare)
    async def select_skincare_product(message: types.Message, state: FSMContext):
        data = await state.get_data()
        selected_products: list = data.get(SELECTED_PRODUCTS)
        valid_button_texts = []
        for row in skincare_kb().keyboard:
            for button in row:
                valid_button_texts.append(button.text)

        if message.text == "/done":
            await message.answer("Your selected skincare products are:")
            for product in selected_products:
                await message.answer(product)
            await message.answer(
                "Do you want to save?", reply_markup=get_yes_change_kb()
            )
            await state.update_data(chosen_skincare=selected_products)
            await state.set_state(StatesMorningSkincare.save_data_in_db)
        elif message.text in valid_button_texts:
            if message.text not in selected_products:
                await state.set_data(
                    {SELECTED_PRODUCTS: [message.text, *selected_products]}
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
                reply_markup=skincare_kb(),
            )

    @router.message(StatesMorningSkincare.save_data_in_db, F.text.casefold() == "yes")
    async def process_final_decision(message: Message, state: FSMContext):
        print(f"{__file__}")
        await save_data(message, state)

    @router.message(
        StatesMorningSkincare.save_data_in_db, F.text.casefold() == "change"
    )
    async def process_final_decision2(message: Message, state: FSMContext):
        await state.clear()
        await start_skincare_selection(message, state)

    return router


async def save_data(message: Message, state: FSMContext):
    user_data = await state.get_data()

    skincare_products_str = ", ".join(user_data.get("chosen_skincare", []))

    with Session() as session:
        try:
            # session.begin()
            user = session.query(User).filter_by(chat_id=message.from_user.id).first()
            user_answer = SkincareCosmetics(
                user_id=user.id,
                skincare=skincare_products_str,
                applied_at=AppliedAt.MORNING,
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
