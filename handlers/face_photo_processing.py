import os
from datetime import datetime
from io import BytesIO

from aiogram import Bot, Router, types
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import FSInputFile, Message
from PIL import Image

from models import FacePhoto, User
from models.models import Session
from utils.face_classification import ProfilePhoto, predict_face_pose

PHOTOS_BY_SIDE = {}


class MorningSkincareStatesGroup(StatesGroup):
    choosing_photo = State()


def make_router(bot: Bot) -> Router:
    router = Router()

    @router.message(StateFilter(None), Command("face_photo"))
    async def start_photo_selection(message: types.Message, state: FSMContext):
        image_example = FSInputFile("content/example_photo.png")
        await message.answer("Please upload or take three photos of your profiles.")
        await message.answer_photo(image_example, caption="Example photos")
        await message.answer(
            "Could you please upload a photo of one side of your face?"
        )
        await state.set_state(MorningSkincareStatesGroup.choosing_photo)

    @router.message(MorningSkincareStatesGroup.choosing_photo)
    async def process_face_photo(message: Message, state: FSMContext, bot: Bot):
        if not message.photo:
            await message.reply("No photo detected. Please upload a photo.")
            return

        photo_data = BytesIO()
        await bot.download(message.photo[-1], destination=photo_data)
        side_photo = predict_face_pose(photo_data)

        if side_photo == ProfilePhoto.LEFT_PROFILE and "left" not in PHOTOS_BY_SIDE:
            user_left_profile_photo = save_photo(message, photo_data, "LEFT")
            PHOTOS_BY_SIDE["left"] = user_left_profile_photo

            if ("right" in PHOTOS_BY_SIDE) and ("full_face" in PHOTOS_BY_SIDE):
                await save_data(message, state, PHOTOS_BY_SIDE)
            else:
                await message.answer("Could you please load next photo of your face? ")
        elif side_photo == ProfilePhoto.RIGHT_PROFILE and "right" not in PHOTOS_BY_SIDE:
            user_right_profile_photo = save_photo(message, photo_data, "RIGHT")
            PHOTOS_BY_SIDE["right"] = user_right_profile_photo

            if ("left" in PHOTOS_BY_SIDE) and ("full_face" in PHOTOS_BY_SIDE):
                await save_data(message, state, PHOTOS_BY_SIDE)
            else:
                await message.answer("Could you please load next photo of your face?")
        elif (
            side_photo == ProfilePhoto.FULL_FACE_PROFILE
            and "full_face" not in PHOTOS_BY_SIDE
        ):
            user_full_face_photo = save_photo(message, photo_data, "FULL_FACE")
            PHOTOS_BY_SIDE["full_face"] = user_full_face_photo

            if ("left" in PHOTOS_BY_SIDE) and ("right" in PHOTOS_BY_SIDE):
                await save_data(message, state, PHOTOS_BY_SIDE)

            else:
                await message.answer(
                    "Could you please upload the next photo of your face?"
                )
        elif side_photo == ProfilePhoto.NO_FACES_DETECTED:
            await message.answer(
                "No faces detected in the photo. Please upload a clear photo."
            )
        else:
            await message.answer(
                "You've already uploaded this side. Please upload a different photo or click /done when finished."
            )

    return router


def create_topic_folder(user_id, topic: str) -> str:
    date_today = datetime.now().strftime("%Y-%m-%d")
    directory_path = f"./data/{user_id}/{date_today}/{topic}"
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)
    return directory_path


def save_photo(message, photo, side) -> str:
    directory_path = create_topic_folder(message.from_user.id, "pimples")
    timestamp = datetime.now().strftime("%Y%m%d_")
    photo_filename = os.path.join(directory_path, f"{timestamp}_{side}.png")
    with open(photo_filename, "wb") as fp:
        im = Image.open(photo)
        im.save(fp)
    return photo_filename


async def save_data(message, state, data: dict):
    with Session() as session:
        try:
            user = session.query(User).filter_by(chat_id=message.from_user.id).first()
            user_answer = FacePhoto(
                user_id=user.id,
                date=datetime.today(),
                photo_left=data.get("left"),
                photo_right=data.get("right"),
                photo_full_face=data.get("full_face"),
            )

            session.add(user_answer)
            session.commit()

            await message.answer("Your photos have been saved. Thank you!")
        except Exception as e:
            session.rollback()
            await message.answer(
                "Sorry, there was an error saving your data.\nYou may have already filled out this form today."
            )
            print(e)
        finally:
            data.clear()
            await state.clear()
