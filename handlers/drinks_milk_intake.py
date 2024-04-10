from datetime import datetime

from aiogram import F, Router, types
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, ReplyKeyboardRemove

from keyboards.drinks_milk import milk_kb
from keyboards.yes_change import get_yes_change_kb
from models import DrinksAppliedAt, DrinksIntake, User
from models.models import Session

router = Router()

SELECTED_MILK = "selected_milk"


class StatesDrinksMilk(StatesGroup):
    choosing_milk = State()
    save_data_in_db = State()


@router.message(StateFilter(None), Command("milk_drinks"))
async def start_milk_selection(message: types.Message, state: FSMContext):
    await state.set_data({SELECTED_MILK: []})

    await message.answer(
        "What kind of milk did you drink today?", reply_markup=milk_kb()
    )
    await state.set_state(StatesDrinksMilk.choosing_milk)


@router.message(StatesDrinksMilk.choosing_milk)
async def select_milk(message: types.Message, state: FSMContext):
    data = await state.get_data()
    selected_products_milk: list = data.get(SELECTED_MILK)
    valid_button_texts = []
    for row in milk_kb().keyboard:
        for button in row:
            valid_button_texts.append(button.text)

    if message.text == "/done":
        await message.answer("Your selected:")
        for product in selected_products_milk:
            await message.answer(product)
        await message.answer("Do you want to save?", reply_markup=get_yes_change_kb())
        await state.update_data(chosen_milk=selected_products_milk)
        await state.set_state(StatesDrinksMilk.save_data_in_db)
    elif message.text in valid_button_texts:
        if message.text not in selected_products_milk:
            await state.set_data(
                {
                    SELECTED_MILK: [
                        message.text,
                        *selected_products_milk,
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
            reply_markup=milk_kb(),
        )


@router.message(StatesDrinksMilk.save_data_in_db, F.text.casefold() == "yes")
async def process_final_decision_yes(message: Message, state: FSMContext):
    await save_data(message, state)


@router.message(StatesDrinksMilk.save_data_in_db, F.text.casefold() == "change")
async def process_final_decision_change(message: Message, state: FSMContext):
    await state.clear()
    await start_milk_selection(message, state)


async def save_data(message: Message, state: FSMContext):
    user_data = await state.get_data()

    drinks_milk_str = ", ".join(user_data.get("chosen_milk", []))

    with Session() as session:
        try:
            # session.begin()
            user = session.query(User).filter_by(chat_id=message.from_user.id).first()
            user_answer = DrinksIntake(
                user_id=user.id,
                drinks=drinks_milk_str,
                drinks_applied_at=DrinksAppliedAt.DRINKS_MILK,
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
