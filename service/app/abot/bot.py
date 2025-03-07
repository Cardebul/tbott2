from aiogram import Bot, Dispatcher
from app.const import TKEY
from app.abot.handlers import cart_router, main_router, profile_router



async def main():
    bot = Bot(token=TKEY)
    dp = Dispatcher()

    dp.include_routers(main_router.router, cart_router.router, profile_router.router)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


