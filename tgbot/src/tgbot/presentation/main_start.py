import os
import asyncio

from aiogram import Bot, Dispatcher
from dishka.integrations.aiogram import setup_dishka

from tgbot.infrastructure import ioc_container_factory
from tgbot.presentation.v2 import (
    start_router,
    farm_stars_router,
    main_router,
    get_link_router,
    reviews_router,
    faq_router,
    boost_router,
    profile_router,
    mini_games_router,
    tasks_router,
    withdraw_router,
    rating_router,
    admin_router,
)
async def on_startup(dp: Dispatcher):
    # Запуск Telethon-клиента в рамках того же event loop
    await admin_router.telethon_client.start()
    print("Telethon клиент запущен!")

async def main():
    bot = Bot(token=os.getenv("BOT_TOKEN"))
    dp = Dispatcher()

    dp.include_router(start_router)
    dp.include_router(farm_stars_router)
    dp.include_router(main_router)
    dp.include_router(get_link_router)
    dp.include_router(reviews_router)
    dp.include_router(faq_router)
    dp.include_router(boost_router)
    dp.include_router(profile_router)
    dp.include_router(mini_games_router)
    dp.include_router(tasks_router)
    dp.include_router(withdraw_router)
    dp.include_router(rating_router)
    dp.include_router(admin_router)
    container = ioc_container_factory()
    setup_dishka(container=container, router=dp)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


asyncio.run(main())
