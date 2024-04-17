import os
from datetime import datetime
from io import BytesIO

from aiogram import Bot, Router, types
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message
from PIL import Image

from utils.face_position import ProfilePhoto, pred_face_pose


class StatesTakePhoto(StatesGroup):
    load_photo = State()
    save_data_in_db = State()


key_photo = {}


def make_router(bot: Bot) -> Router:
    router = Router()

    @router.message(StateFilter(None), Command("face_photo"))
    async def start_select_photo(message: types.Message, state: FSMContext):
        await message.answer("Could you please load the one side of your face?")
        await state.set_state(StatesTakePhoto.load_photo)

    @router.message(StatesTakePhoto.load_photo)
    async def process_photo(message: Message, state: FSMContext, bot: Bot):
        if not message.photo:
            await message.reply("No photo detected, please upload a photo.")
            return

        obj = BytesIO()
        await bot.download(message.photo[-1], destination=obj)
        side_photo = pred_face_pose(obj)

        if side_photo == ProfilePhoto.LEFT_PROFILE and "left" not in key_photo:
            user_left_profile_photo = save_photo(message, obj, "LEFT")
            key_photo["left"] = user_left_profile_photo
            print(key_photo)
            if ("right" in key_photo) and ("full_face" in key_photo):
                await message.answer("All photo was saved, thanks!")
                await state.clear()
                key_photo.clear()
            else:
                await message.answer("Could you please load next photo of your face? ")
        elif side_photo == ProfilePhoto.RIGHT_PROFILE and "right" not in key_photo:
            user_right_profile_photo = save_photo(message, obj, "RIGHT")
            key_photo["right"] = user_right_profile_photo
            print(key_photo)
            if ("left" in key_photo) and ("full_face" in key_photo):
                await message.answer("All photo was saved, thanks!")
                await state.clear()
                key_photo.clear()
            else:
                await message.answer("Could you please load next photo of your face?")
        elif (
            side_photo == ProfilePhoto.FULL_FACE_PROFILE
            and "full_face" not in key_photo
        ):
            user_full_face_photo = save_photo(message, obj, "FULL_FACE")
            key_photo["full_face"] = user_full_face_photo
            print(key_photo)
            if ("left" in key_photo) and ("right" in key_photo):
                await message.answer("All photo was saved, thanks!")
                await state.clear()
                key_photo.clear()
            else:
                await message.answer("Could you please load next photo of your face?")
        elif side_photo == ProfilePhoto.NO_FACES_DETECTED:
            await message.answer(
                "Could you please load next photo of your face?\nYou are already have this side."
            )
        else:
            await message.answer("No photo detected face, please upload a photo.")

    return router


def create_topic_folder(user_id, topic: str) -> str:
    date_today = datetime.now().strftime("%Y-%m-%d")
    directory_path = f"./data/{user_id}/{date_today}/{topic}"
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)
    return directory_path


def save_photo(message, photo, side) -> str:
    directory_path = create_topic_folder(message.from_user.id, "pimples")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S%f")
    name_photo = os.path.join(directory_path, f"{timestamp}_{side}.png")
    with open(name_photo, "wb") as fp:
        im = Image.open(photo)
        im.save(fp)
    return name_photo
