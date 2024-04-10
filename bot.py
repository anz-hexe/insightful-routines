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
    pimples,
    snacks_intake,
    stress_level,
    supplements_intake,
    water_intake,
    welcome,
    workouts,
)
from models.models import init_db


async def main():
    init_db()

    config = Config()

    bot = Bot(token=config.api_token.get_secret_value())
    dp = Dispatcher()

    dp.include_router(welcome.router)
    dp.include_router(first_meet.router)
    dp.include_router(mornig_skincare.router)
    dp.include_router(evening_skincare.router)
    dp.include_router(food_intake_breakfast.router)
    dp.include_router(food_intake_lunch.router)
    dp.include_router(food_intake_dinner.router)
    dp.include_router(drinks_hot_intake.router)
    dp.include_router(drinks_other_intake.router)
    dp.include_router(drinks_milk_intake.router)
    dp.include_router(snacks_intake.router)
    dp.include_router(stress_level.router)
    dp.include_router(supplements_intake.router)
    dp.include_router(workouts.router)
    dp.include_router(water_intake.router)
    dp.include_router(pimples.make_router(bot))

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO, format="%(message)s", handlers=[RichHandler()]
    )
    asyncio.run(main())
