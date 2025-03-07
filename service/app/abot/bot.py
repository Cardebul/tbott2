from aiogram import Bot, Dispatcher
from app.abot.handlers import main_router, cart_router, profile_router


async def main():
    bot = Bot(token="12312312321")
    dp = Dispatcher()

    dp.include_routers(main_router.router, cart_router.router, profile_router.router)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


