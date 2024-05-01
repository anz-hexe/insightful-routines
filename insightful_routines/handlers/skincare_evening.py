from datetime import datetime

from aiogram import Bot, F, Router, types
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, ReplyKeyboardMarkup, ReplyKeyboardRemove
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from keyboards.yes_change import get_yes_change_kb
from models import EveningSkincare, User
from models.models import Session

SELECTED_SKINCARE_PRODUCTS = "selected_products"


class EveningSkincareStateGroup(StatesGroup):
    choosing_skincare = State()
    saving_data_in_db = State()


def create_evening_skincare_keyboard() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.button(text="cleaner")
    kb.button(text="tonic")
    kb.button(text="serum")
    kb.button(text="eye cream")
    kb.button(text="cream")
    kb.button(text="patch")
    kb.button(text="eye patchs")
    kb.button(text="sunscreen")
    kb.button(text="pilling")
    kb.button(text="scrub")
    kb.button(text="spot cream")
    kb.button(text="mask")
    kb.button(text="skin picking(")
    kb.button(text="nothing")
    # TODO
    # kb.button(text="done")
    kb.adjust(2)
    return kb.as_markup(resize_keyboard=True)


def make_router(bot: Bot) -> Router:
    router = Router()

    @router.message(StateFilter(None), Command("evening_skincare"))
    async def start_evening_skincare_selection(
        message: types.Message, state: FSMContext
    ):
        await state.set_data({SELECTED_SKINCARE_PRODUCTS: []})

        await message.answer(
            "What skin products did you use this evening?",
            reply_markup=create_evening_skincare_keyboard(),
        )
        await state.set_state(EveningSkincareStateGroup.choosing_skincare)

    @router.message(EveningSkincareStateGroup.choosing_skincare)
    async def handle_evening_skincare_selection(
        message: types.Message, state: FSMContext
    ):
        data = await state.get_data()
        selected_products: list = data.get(SELECTED_SKINCARE_PRODUCTS)
        valid_options = []
        for row in create_evening_skincare_keyboard().keyboard:
            for button in row:
                valid_options.append(button.text)

        if message.text == "/done":
            await message.answer("Your selected skincare products are:")
            for product in selected_products:
                await message.answer(product)
            await message.answer(
                "Do you want to save?", reply_markup=get_yes_change_kb()
            )
            await state.update_data(chosen_skincare=selected_products)
            await state.set_state(EveningSkincareStateGroup.saving_data_in_db)
        elif message.text in valid_options:
            if message.text not in selected_products:
                await state.set_data(
                    {SELECTED_SKINCARE_PRODUCTS: [message.text, *selected_products]}
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
                reply_markup=create_evening_skincare_keyboard(),
            )

    @router.message(
        EveningSkincareStateGroup.saving_data_in_db, F.text.casefold() == "yes"
    )
    async def save_evening_skincare_data(message: Message, state: FSMContext):
        print(f"{__file__}")
        await save_evening_skincare(message, state)

    @router.message(
        EveningSkincareStateGroup.saving_data_in_db, F.text.casefold() == "change"
    )
    async def change_evening_skincare_selection(message: Message, state: FSMContext):
        await state.clear()
        await start_evening_skincare_selection(message, state)

    return router


async def save_evening_skincare(message: Message, state: FSMContext):
    user_data = await state.get_data()

    evening_skincare_str = ", ".join(user_data.get("chosen_skincare", []))

    with Session() as session:
        try:
            user = session.query(User).filter_by(chat_id=message.from_user.id).first()
            evening_skincare_entry = EveningSkincare(
                user_id=user.id,
                evening_skincare=evening_skincare_str,
                date=datetime.today(),
            )
            session.add(evening_skincare_entry)
            print(evening_skincare_entry)

            session.commit()

            await message.answer(
                "Your data has been saved. Thank you!",
                reply_markup=ReplyKeyboardRemove(),
            )
        except Exception as e:
            session.rollback()
            await message.answer(
                "Sorry, there was an error saving your data. \n"
                "You may have already filled out this form today.",
                reply_markup=ReplyKeyboardRemove(),
            )
            print(e)
        finally:
            await state.clear()
