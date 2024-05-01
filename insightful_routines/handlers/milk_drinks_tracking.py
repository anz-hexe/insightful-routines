from aiogram import Bot, F, Router, types
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, ReplyKeyboardMarkup, ReplyKeyboardRemove
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from insightful_routines.keyboards.yes_change import get_yes_change_kb
from insightful_routines.models import MilkDrinksIntake, User
from insightful_routines.models.models import Session

SELECTED_MILK_DRINKS = "selected_milk"


class MilkDrinksStateGroup(StatesGroup):
    choosing_milk = State()
    save_data_in_db = State()


def create_milk_drinks_keyboard() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.button(text="yes, cow")
    kb.button(text="yes, lactose free")
    kb.button(text="yes, alternative")
    kb.button(text="no")
    kb.adjust(2)
    return kb.as_markup(resize_keyboard=True)


def make_router(bot: Bot) -> Router:
    router = Router()

    @router.message(StateFilter(None), Command("milk_drinks"))
    async def start_milk_drinks_selection(message: types.Message, state: FSMContext):
        await state.set_data({SELECTED_MILK_DRINKS: []})

        await message.answer(
            "What kind of milk did you drink today?",
            reply_markup=create_milk_drinks_keyboard(),
        )
        await state.set_state(MilkDrinksStateGroup.choosing_milk)

    @router.message(MilkDrinksStateGroup.choosing_milk)
    async def handle_milk_drinks_selection(message: types.Message, state: FSMContext):
        data = await state.get_data()
        selected_products_milk: list = data.get(SELECTED_MILK_DRINKS)
        valid_button_texts = []
        for row in create_milk_drinks_keyboard().keyboard:
            for button in row:
                valid_button_texts.append(button.text)

        if message.text == "/done":
            await message.answer("Your selected drinks:")
            for product in selected_products_milk:
                await message.answer(product)
            await message.answer(
                "Do you want to save?", reply_markup=get_yes_change_kb()
            )
            await state.update_data(chosen_milk=selected_products_milk)
            await state.set_state(MilkDrinksStateGroup.save_data_in_db)
        elif message.text in valid_button_texts:
            if message.text not in selected_products_milk:
                await state.set_data(
                    {
                        SELECTED_MILK_DRINKS: [
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
                reply_markup=create_milk_drinks_keyboard(),
            )

    @router.message(MilkDrinksStateGroup.save_data_in_db, F.text.casefold() == "yes")
    async def save_milk_drinks_data(message: Message, state: FSMContext):
        await save_milk_drinks(message, state)

    @router.message(MilkDrinksStateGroup.save_data_in_db, F.text.casefold() == "change")
    async def change_milk_drinks_selection(message: Message, state: FSMContext):
        await state.clear()
        await start_milk_drinks_selection(message, state)

    return router


async def save_milk_drinks(message: Message, state: FSMContext):
    user_data = await state.get_data()

    milk_drinks_str = ", ".join(user_data.get("chosen_milk", []))

    with Session() as session:
        try:
            user = session.query(User).filter_by(chat_id=message.from_user.id).first()
            milk_drinks_intake = MilkDrinksIntake(
                user_id=user.id,
                milk_drinks=milk_drinks_str,
            )

            session.add(milk_drinks_intake)

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
