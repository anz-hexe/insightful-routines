from datetime import datetime

from aiogram import Bot, F, Router, types
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, ReplyKeyboardMarkup, ReplyKeyboardRemove
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from keyboards.yes_change import get_yes_change_kb
from models import OtherDrinksIntake, User
from models.models import Session

SELECTED_OTHER_DRINKS = "selected_other_drinks"


class OtherDrinksStateGroup(StatesGroup):
    choosing_other_drinks = State()
    save_data_in_db = State()


def create_other_drinks_keyboard() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.button(text="alcohol")
    kb.button(text="energy drink")
    kb.button(text="juice")
    kb.button(text="soft drink")
    kb.button(text="sparkling mineral water")
    kb.button(text="no")
    # TODO
    # kb.button(text="other")
    kb.adjust(2)
    return kb.as_markup(resize_keyboard=True)


def make_router(bot: Bot) -> Router:
    router = Router()

    @router.message(StateFilter(None), Command("other_drinks"))
    async def start_other_drinks_selection(message: types.Message, state: FSMContext):
        await state.set_data({SELECTED_OTHER_DRINKS: []})

        await message.answer(
            "What other drinks did you drink today?",
            reply_markup=create_other_drinks_keyboard(),
        )
        await state.set_state(OtherDrinksStateGroup.choosing_other_drinks)

    @router.message(OtherDrinksStateGroup.choosing_other_drinks)
    async def handle_other_drinks_selection(message: types.Message, state: FSMContext):
        data = await state.get_data()
        selected_other_drinks: list = data.get(SELECTED_OTHER_DRINKS)
        valid_options = []
        for row in create_other_drinks_keyboard().keyboard:
            for button in row:
                valid_options.append(button.text)

        if message.text == "/done":
            await message.answer("Your selected:")
            for product in selected_other_drinks:
                await message.answer(product)
            await message.answer(
                "Do you want to save?", reply_markup=get_yes_change_kb()
            )
            await state.update_data(chosen_other_drinks=selected_other_drinks)
            await state.set_state(OtherDrinksStateGroup.save_data_in_db)
        elif message.text in valid_options:
            if message.text not in selected_other_drinks:
                await state.set_data(
                    {
                        SELECTED_OTHER_DRINKS: [
                            message.text,
                            *selected_other_drinks,
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
                reply_markup=create_other_drinks_keyboard(),
            )

    @router.message(OtherDrinksStateGroup.save_data_in_db, F.text.casefold() == "yes")
    async def save_other_drinks_data(message: Message, state: FSMContext):
        await save_other_drinks(message, state)

    @router.message(
        OtherDrinksStateGroup.save_data_in_db, F.text.casefold() == "change"
    )
    async def change_other_drinks_selection(message: Message, state: FSMContext):
        await state.clear()
        await start_other_drinks_selection(message, state)

    return router


async def save_other_drinks(message: Message, state: FSMContext):
    user_data = await state.get_data()

    other_drinks_str = ", ".join(user_data.get("chosen_other_drinks", []))

    with Session() as session:
        try:
            user = session.query(User).filter_by(chat_id=message.from_user.id).first()
            other_drinks_intake = OtherDrinksIntake(
                user_id=user.id,
                other_drinks=other_drinks_str,
                date=datetime.today(),
            )

            session.add(other_drinks_intake)

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
