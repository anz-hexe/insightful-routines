from datetime import datetime

from aiogram import Bot, F, Router, types
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, ReplyKeyboardMarkup, ReplyKeyboardRemove
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from insightful_routines.keyboards.yes_change import get_yes_change_kb
from insightful_routines.models import HotDrinksIntake, User
from insightful_routines.models.models import Session

SELECTED_HOT_DRINKS = "selected_drinks_hot"


class HotDrinksStateGroup(StatesGroup):
    selecting_drinks = State()
    saving_data_in_db = State()


def create_hot_drinks_keyboard() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.button(text="green tea")
    kb.button(text="black tea")
    kb.button(text="coffee")
    kb.button(text="herbal tea")
    kb.button(text="other")
    kb.button(text="no")
    # TODO
    # kb.button(text="other, please enter")
    kb.adjust(2)
    return kb.as_markup(resize_keyboard=True)


def make_router(bot: Bot) -> Router:
    router = Router()

    @router.message(StateFilter(None), Command("hot_drinks"))
    async def start_hot_drinks_selection(message: types.Message, state: FSMContext):
        await state.set_data({SELECTED_HOT_DRINKS: []})

        await message.answer(
            "What hot drinks did you drink today?",
            reply_markup=create_hot_drinks_keyboard(),
        )
        await state.set_state(HotDrinksStateGroup.selecting_drinks)

    @router.message(HotDrinksStateGroup.selecting_drinks)
    async def handle_hot_drinks_selection(message: types.Message, state: FSMContext):
        data = await state.get_data()
        selected_hot_drinks: list = data.get(SELECTED_HOT_DRINKS)
        valid_options = []
        for row in create_hot_drinks_keyboard().keyboard:
            for button in row:
                valid_options.append(button.text)

        if message.text == "/done":
            await message.answer("Your selected drinks:")
            for product in selected_hot_drinks:
                await message.answer(product)
            await message.answer(
                "Do you want to save?", reply_markup=get_yes_change_kb()
            )
            await state.update_data(chosen_drinks_hot=selected_hot_drinks)
            await state.set_state(HotDrinksStateGroup.saving_data_in_db)
        elif message.text in valid_options:
            if message.text not in selected_hot_drinks:
                await state.set_data(
                    {
                        SELECTED_HOT_DRINKS: [
                            message.text,
                            *selected_hot_drinks,
                        ]
                    }
                )
                await message.answer(
                    f"You selected: {message.text}. Select more or click /done when finished."
                )
            else:
                await message.answer(
                    "You have already selected this drink. Please select another or click /done when finished."
                )
        else:
            await message.answer(
                "Please select from the list or click /done when finished.",
                reply_markup=create_hot_drinks_keyboard(),
            )

    @router.message(HotDrinksStateGroup.saving_data_in_db, F.text.casefold() == "yes")
    async def save_hot_drinks_data(message: Message, state: FSMContext):
        await save_hot_drinks(message, state)

    @router.message(
        HotDrinksStateGroup.saving_data_in_db, F.text.casefold() == "change"
    )
    async def change_hot_drinks_selection(message: Message, state: FSMContext):
        await state.clear()
        await start_hot_drinks_selection(message, state)

    return router


async def save_hot_drinks(message: Message, state: FSMContext):
    user_data = await state.get_data()

    hot_drinks_str = ", ".join(user_data.get("chosen_drinks_hot", []))

    with Session() as session:
        try:
            user = session.query(User).filter_by(chat_id=message.from_user.id).first()
            hot_drinks_intake = HotDrinksIntake(
                user_id=user.id,
                hot_drinks=hot_drinks_str,
                date=datetime.today(),
            )

            print(hot_drinks_intake)

            session.add(hot_drinks_intake)

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
