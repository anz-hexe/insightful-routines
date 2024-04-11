import os

from aiogram import Bot, Router
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardRemove

from models import User
from models.models import Session


def make_router(bot: Bot) -> Router:
    router = Router()

    @router.message(Command("start"))
    async def welcome(message: Message):
        session = Session()
        existing_user = (
            session.query(User).filter_by(chat_id=message.from_user.id).first()
        )

        if not existing_user:
            new_user = User(
                username=message.from_user.username, chat_id=message.from_user.id
            )
            session.add(new_user)
            session.commit()
            await message.answer(
                "Welcome! Let's get to know each other better! \n "
                "Please fill out the form by clicking on the first meeting below. \n\n"
                "/first_meeting",
                reply_markup=ReplyKeyboardRemove(),
            )
            create_new_user_folder(new_user.chat_id)
        else:
            await message.answer(
                "Welcome back!\n\n Please use the menu to fill out forms."
            )
        session.close()

    return router


def create_new_user_folder(new_user_id):
    directory_path = f"./data/{new_user_id}//"

    if not os.path.exists(directory_path):
        os.makedirs(directory_path)
