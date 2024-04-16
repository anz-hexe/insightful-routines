import os
from datetime import datetime

from aiogram import Bot, F, Router, types
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, ReplyKeyboardRemove

from keyboards.photo import photo_kb
from utils.face_position import ProfilePhoto, pred_face_pose


class StatesTakePhoto(StatesGroup):
    load_photo = State()
    left_profile = State()
    right_profile = State()
    right_profile_load = State()
    full_face = State()
    full_face_load = State()
    save_data_in_db = State()


def make_router(bot: Bot) -> Router:
    router = Router()

    @router.message(StateFilter(None), Command("face_photo"))
    async def start_select_photo(message: types.Message, state: FSMContext):
        await message.answer(
            "Is your photo in preview mode or in reverse mode?",
            reply_markup=photo_kb(),
        )
        await state.set_state(StatesTakePhoto.load_photo)

    @router.message(StatesTakePhoto.load_photo, F.text.casefold() == "reverse")
    async def process_reverse_left_side(message: Message, state: FSMContext):
        await message.answer(
            "Load left photo",
            reply_markup=ReplyKeyboardRemove(),
        )
        await state.set_state(StatesTakePhoto.left_profile)

    @router.message(StatesTakePhoto.left_profile)
    async def load_reverse_left_side(message: Message, state: FSMContext, bot: Bot):
        if not message.photo:
            await message.reply("No photo detected, please upload a photo.")
            return

        directory_path = create_topic_folder(message.from_user.id, "pimples")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S%f")
        name_photo = os.path.join(directory_path, f"{timestamp}.png")

        await bot.download(message.photo[-1], destination=name_photo)

        side_photo = pred_face_pose(name_photo)

        if side_photo == ProfilePhoto.LEFT_PROFILE:
            await message.answer("good")
            await state.set_state(StatesTakePhoto.right_profile_load)
            await message.answer("Load right photo")
        else:
            await message.answer("please load other photo left side again")
            delete_photo(name_photo)
            process_reverse_left_side(message, state)

    @router.message(StatesTakePhoto.right_profile_load)
    async def load_reverse_right_side(message: Message, state: FSMContext, bot: Bot):
        if not message.photo:
            await message.reply("No photo detected, please upload a photo.")
            return

        directory_path = create_topic_folder(message.from_user.id, "pimples")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S%f")
        name_photo = os.path.join(directory_path, f"{timestamp}.png")

        await bot.download(message.photo[-1], destination=name_photo)

        right_side_photo = pred_face_pose(name_photo)

        if right_side_photo == ProfilePhoto.RIGHT_PROFILE:
            await message.answer("good")
            await state.set_state(StatesTakePhoto.full_face_load)
            await message.answer("Load full face photo")
        else:
            await message.answer("please load other photo right side again")
            delete_photo(name_photo)
            load_reverse_right_side(message, state, bot)

    @router.message(StatesTakePhoto.full_face_load)
    async def load_reverse_full_face_side(
        message: Message, state: FSMContext, bot: Bot
    ):
        if not message.photo:
            await message.reply("No photo detected, please upload a photo.")
            return

        directory_path = create_topic_folder(message.from_user.id, "pimples")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S%f")
        name_photo = os.path.join(directory_path, f"{timestamp}.png")

        await bot.download(message.photo[-1], destination=name_photo)

        full_face_side_photo = pred_face_pose(name_photo)

        if full_face_side_photo == ProfilePhoto.FULL_FACE_PROFILE:
            await message.answer("good")
            await state.set_state(StatesTakePhoto.full_face_load)
            await message.answer(
                "Photos saved successfully!\n Please use the menu to fill out forms."
            )
            await state.clear()
        else:
            await message.answer("please load other photo full face side again")
            delete_photo(name_photo)
            load_reverse_full_face_side(message, state, bot)

    # # ---------------------------------------------

    @router.message(StatesTakePhoto.load_photo, F.text.casefold() == "preview")
    async def process_preview_left_side(message: Message, state: FSMContext):
        await message.answer(
            "Load left photo",
            reply_markup=ReplyKeyboardRemove(),
        )
        await state.set_state(StatesTakePhoto.left_profile)

    @router.message(StatesTakePhoto.left_profile)
    async def load_preview_left_side(message: Message, state: FSMContext, bot: Bot):
        if not message.photo:
            await message.reply("No photo detected, please upload a photo.")
            return

        directory_path = create_topic_folder(message.from_user.id, "pimples")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S%f")
        name_photo = os.path.join(directory_path, f"{timestamp}.png")

        await bot.download(message.photo[-1], destination=name_photo)

        side_photo = pred_face_pose(name_photo)

        if side_photo == ProfilePhoto.RIGHT_PROFILE:
            await message.answer("good")
            await state.set_state(StatesTakePhoto.right_profile_load)
            await message.answer("Load right photo")
        else:
            await message.answer("please load other photo left side again")
            delete_photo(name_photo)
            process_preview_left_side(message, state)

    @router.message(StatesTakePhoto.right_profile_load)
    async def load_preview_right_side(message: Message, state: FSMContext, bot: Bot):
        if not message.photo:
            await message.reply("No photo detected, please upload a photo.")
            return

        directory_path = create_topic_folder(message.from_user.id, "pimples")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S%f")
        name_photo = os.path.join(directory_path, f"{timestamp}.png")

        await bot.download(message.photo[-1], destination=name_photo)

        right_side_photo = pred_face_pose(name_photo)

        if right_side_photo == ProfilePhoto.LEFT_PROFILE:
            await message.answer("good")
            await state.set_state(StatesTakePhoto.full_face_load)
            await message.answer("Load full face photo")
        else:
            await message.answer("please load other photo right side again")
            delete_photo(name_photo)
            load_preview_right_side(message, state, bot)

    @router.message(StatesTakePhoto.full_face_load)
    async def load_preview_full_face_side(
        message: Message, state: FSMContext, bot: Bot
    ):
        if not message.photo:
            await message.reply("No photo detected, please upload a photo.")
            return

        directory_path = create_topic_folder(message.from_user.id, "pimples")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S%f")
        name_photo = os.path.join(directory_path, f"{timestamp}.png")

        await bot.download(message.photo[-1], destination=name_photo)

        full_face_side_photo = pred_face_pose(name_photo)

        if full_face_side_photo == ProfilePhoto.FULL_FACE_PROFILE:
            await message.answer("good")
            await state.set_state(StatesTakePhoto.full_face_load)
            await message.answer(
                "Photos saved successfully!\n Please use the menu to fill out forms."
            )
            await state.clear()
        else:
            await message.answer("please load other photo full face side again")
            delete_photo(name_photo)
            load_preview_full_face_side(message, state, bot)

    return router


def create_topic_folder(user_id, topic: str) -> str:
    date_today = datetime.now().strftime("%Y-%m-%d")
    directory_path = f"./data/{user_id}/{date_today}/{topic}"
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)
    return directory_path


def delete_photo(filename: str):
    try:
        os.remove(filename)
        return True
    except OSError as e:
        print(f"Error deleting photo: {e}")
        return False
