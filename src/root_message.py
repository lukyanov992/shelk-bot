from __future__ import annotations
from typing import Optional, Dict

from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import Message, InlineKeyboardMarkup

# Память на процесс: chat_id -> message_id корневого сообщения
_ROOT_IDS: Dict[int, int] = {}

async def get_root_id(chat_id: int) -> Optional[int]:
    return _ROOT_IDS.get(chat_id)

async def set_root(msg: Message) -> None:
    _ROOT_IDS[msg.chat.id] = msg.message_id

async def ensure_root(message: Message, text: str = "Загрузка…",
                      reply_markup: Optional[InlineKeyboardMarkup] = None,
                      parse_mode: Optional[str] = "HTML") -> int:
    """
    Гарантирует, что в чате есть одно корневое сообщение бота.
    Если нет — создаёт; если есть — редактирует.
    Возвращает message_id корневого сообщения.
    """
    bot: Bot = message.bot
    chat_id = message.chat.id
    msg_id = _ROOT_IDS.get(chat_id)

    if msg_id:
        try:
            await bot.edit_message_text(
                chat_id=chat_id,
                message_id=msg_id,
                text=text,
                reply_markup=reply_markup,
                parse_mode=parse_mode
            )
            return msg_id
        except TelegramBadRequest as e:
            # Например: "message to edit not found" — сообщение было удалено
            if "message to edit not found" not in str(e).lower():
                # Игнорируем "message is not modified", остальное пробуем пересоздать
                if "message is not modified" in str(e).lower():
                    return msg_id
            # Падаем вниз — пересоздадим root
    # Создаём новое корневое
    root = await bot.send_message(
        chat_id=chat_id,
        text=text,
        reply_markup=reply_markup,
        parse_mode=parse_mode
    )
    _ROOT_IDS[chat_id] = root.message_id
    return root.message_id

async def render(message: Message, text: str,
                 reply_markup: Optional[InlineKeyboardMarkup] = None,
                 parse_mode: Optional[str] = "HTML") -> None:
    """
    Универсальная функция рендера: всегда редактирует одно корневое сообщение.
    Никаких точек и дубликатов сообщений.
    """
    await ensure_root(message, "Загрузка…")
    bot: Bot = message.bot
    chat_id = message.chat.id
    msg_id = _ROOT_IDS[chat_id]
    try:
        await bot.edit_message_text(
            chat_id=chat_id,
            message_id=msg_id,
            text=text,
            reply_markup=reply_markup,
            parse_mode=parse_mode
        )
    except TelegramBadRequest as e:
        # Если вдруг "message to edit not found" — пересоздадим и повторим
        if "message to edit not found" in str(e).lower():
            new_id = await ensure_root(message, text, reply_markup, parse_mode)
            _ROOT_IDS[chat_id] = new_id
        elif "message is not modified" in str(e).lower():
            pass
        else:
            raise
