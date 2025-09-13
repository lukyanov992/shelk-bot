from __future__ import annotations
import asyncio
import logging
import os
import importlib

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

from .middlewares.commands_cleanup import CommandsCleanupMiddleware
from .routers import start as start_router
from .db import init_db

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("src.app")

def make_bot() -> Bot:
    token = os.getenv("BOT_TOKEN")
    if not token:
        raise RuntimeError("Set BOT_TOKEN in environment or .env")
    return Bot(token=token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

def _include(dp: Dispatcher, module_name: str) -> None:
    try:
        mod = importlib.import_module(f"src.routers.{module_name}")
        router = getattr(mod, "router", None)
        if router is None:
            raise AttributeError("module has no attribute 'router'")
        dp.include_router(router)
        log.info("Router connected: %s", module_name)
    except Exception as e:
        log.warning("Router '%s' not connected: %s", module_name, e)

def make_dispatcher() -> Dispatcher:
    dp = Dispatcher()
    dp.message.middleware(CommandsCleanupMiddleware())
    dp.include_router(start_router.router)

    # Подключаем регистрацию (обязательна для работы кнопки «Продолжить»)
    _include(dp, "registration")

    # Если есть другие модули — можно подключить: _include(dp, "misc")
    return dp

async def main() -> None:
    init_db()
    bot = make_bot()
    dp = make_dispatcher()

    # Разрешаем нужные типы апдейтов явно
    used = set(dp.resolve_used_update_types())
    used.update({"message", "callback_query"})
    allowed = sorted(used)
    logging.info("Allowed updates: %s", allowed)

    await dp.start_polling(bot, allowed_updates=allowed)

if __name__ == "__main__":
    asyncio.run(main())
