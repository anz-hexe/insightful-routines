import asyncio
import logging

from aiogram import Bot, Dispatcher
from rich.logging import RichHandler

from config import Config
from handlers import (
    drinks_hot_intake,
    drinks_milk_intake,
    drinks_other_intake,
    evening_skincare,
    first_meet,
    food_intake_breakfast,
    food_intake_dinner,
    food_intake_lunch,
    mornig_skincare,
    photo_face,
    pimples,
    report,
    snacks_intake,
    stress_level,
    supplements_intake,
    water_intake,
    welcome,
    workouts,
)
from models.models import init_db
from settings import create_data_folder


async def main():
    create_data_folder("data")
    init_db()

    config = Config()

    bot = Bot(token=config.api_token.get_secret_value())
    dp = Dispatcher()

    dp.include_router(welcome.make_router(bot))
    dp.include_router(first_meet.make_router(bot))
    dp.include_router(mornig_skincare.make_router(bot))
    dp.include_router(evening_skincare.make_router(bot))
    dp.include_router(food_intake_breakfast.make_router(bot))
    dp.include_router(food_intake_lunch.make_router(bot))
    dp.include_router(food_intake_dinner.make_router(bot))
    dp.include_router(drinks_hot_intake.make_router(bot))
    dp.include_router(drinks_other_intake.make_router(bot))
    dp.include_router(drinks_milk_intake.make_router(bot))
    dp.include_router(snacks_intake.make_router(bot))
    dp.include_router(stress_level.make_router(bot))
    dp.include_router(supplements_intake.make_router(bot))
    dp.include_router(workouts.make_router(bot))
    dp.include_router(water_intake.make_router(bot))
    dp.include_router(pimples.make_router(bot))
    dp.include_router(photo_face.make_router(bot))
    dp.include_router(report.make_router(bot))

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO, format="%(message)s", handlers=[RichHandler()]
    )
    asyncio.run(main())
