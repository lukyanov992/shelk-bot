from __future__ import annotations
from typing import Callable, Awaitable, Any

from aiogram import BaseMiddleware
from aiogram.types import Message, TelegramObject

class CommandsCleanupMiddleware(BaseMiddleware):
    """
    Мидлварь мягко удаляет входящие команды пользователя,
    НО НЕ ПРЕРЫВАЕТ обработку — хэндлеры (например /start) всё равно выполняются.
    Это позволяет рендерить наше корневое сообщение.
    """
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict], Awaitable[Any]],
        event: TelegramObject,
        data: dict
    ) -> Any:
        if isinstance(event, Message):
            text = event.text or ""
            has_cmd = any((e.type == "bot_command") for e in (event.entities or []))
            if text.startswith("/") or has_cmd:
                try:
                    # удаляем сообщение пользователя
                    await event.delete()
                except Exception:
                    pass
                # НЕ возвращаем! Пускаем дальше — чтобы сработал handler (например /start)
                # Можно пометить в data, если пригодится в будущем:
                data["__deleted_command__"] = True

        return await handler(event, data)
