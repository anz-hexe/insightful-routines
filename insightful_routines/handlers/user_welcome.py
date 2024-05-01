import os
from datetime import datetime

from aiogram import Bot, Router
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardRemove

from insightful_routines.models import User
from insightful_routines.models.models import Session


def make_router(bot: Bot) -> Router:
    router = Router()

    @router.message(Command("start"))
    async def welcome(message: Message):
        session = Session()
        try:
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
                    "Welcome! Let's get to know each other better! \n"
                    "Please fill out the form by clicking on the first meeting below. \n\n"
                    "/first_meeting",
                    reply_markup=ReplyKeyboardRemove(),
                )

                create_user_folder_structure(new_user.chat_id)
            else:
                await message.answer(
                    "Welcome back!\n\n Please use the menu to fill out forms."
                )

            create_today_folder(
                existing_user.chat_id if existing_user else new_user.chat_id
            )
        except Exception as e:
            session.rollback()
            print(f"An error occurred: {e}")
        finally:
            session.close()

    return router


def create_user_folder_structure(user_id: int):
    base_path = f"./data/{user_id}/"

    if not os.path.exists(base_path):
        os.makedirs(base_path)


def create_today_folder(user_id: int):
    today = datetime.now().strftime("%Y-%m-%d")
    today_path = f"./data/{user_id}/{today}/"

    if not os.path.exists(today_path):
        os.makedirs(today_path)
