import asyncio
import logging

from aiogram import Bot, Dispatcher
from rich.logging import RichHandler

from config import Config
from handlers import (
    breakfast_food_intake,
    dinner_food_intake,
    face_photo_processing,
    hot_drinks_tracking,
    lunch_food_intake,
    milk_drinks_tracking,
    other_drinks_tracking,
    pimple_tracking,
    skincare_evening,
    skincare_morning,
    snack_tracking,
    stress_tracking,
    supplement_tracking,
    user_onboarding,
    user_report,
    user_welcome,
    water_tracking,
    workout_tracking,
)
from models.models import init_db
from settings import create_data_folder


async def main():
    create_data_folder("data")
    init_db()

    config = Config()

    bot = Bot(token=config.api_token.get_secret_value())
    dp = Dispatcher()

    dp.include_router(user_welcome.make_router(bot))
    dp.include_router(user_onboarding.make_router(bot))
    dp.include_router(skincare_morning.make_router(bot))
    dp.include_router(skincare_evening.make_router(bot))
    dp.include_router(breakfast_food_intake.make_router(bot))
    dp.include_router(lunch_food_intake.make_router(bot))
    dp.include_router(dinner_food_intake.make_router(bot))
    dp.include_router(hot_drinks_tracking.make_router(bot))
    dp.include_router(other_drinks_tracking.make_router(bot))
    dp.include_router(milk_drinks_tracking.make_router(bot))
    dp.include_router(snack_tracking.make_router(bot))
    dp.include_router(stress_tracking.make_router(bot))
    dp.include_router(supplement_tracking.make_router(bot))
    dp.include_router(workout_tracking.make_router(bot))
    dp.include_router(water_tracking.make_router(bot))
    dp.include_router(pimple_tracking.make_router(bot))
    dp.include_router(face_photo_processing.make_router(bot))
    dp.include_router(user_report.make_router(bot))

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO, format="%(message)s", handlers=[RichHandler()]
    )
    asyncio.run(main())
