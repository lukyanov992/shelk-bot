import asyncio
import atexit
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage

from .config import BOT_TOKEN
from .db import init_db
from .utils import obtain_lock_or_exit
from .handlers import start as h_start, callbacks as h_callbacks, messages as h_messages
from .handlers import other as h_other

async def create_app():
    # инициализация
    init_db()
    obtain_lock_or_exit()

    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher(storage=MemoryStorage())

    # Подключаем роутеры
    dp.include_router(h_start.router)
    dp.include_router(h_callbacks.router)
    dp.include_router(h_messages.router)
    dp.include_router(h_other.router)

    async def run_polling_forever():
        # Убрать webhook (аналог твоей функции force_remove_webhook)
        try:
            await bot.delete_webhook(drop_pending_updates=True)
        except Exception:
            pass

        while True:
            try:
                await dp.start_polling(bot)
            except Exception as e:
                print(f"[polling crash] {e}. Перезапуск через 3с…")
                await asyncio.sleep(3)

    return dp, bot, run_polling_forever
