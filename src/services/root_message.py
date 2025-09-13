from __future__ import annotations
from typing import Optional, Dict, Union

from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import Message, InlineKeyboardMarkup, CallbackQuery

from ..db import get_user, upsert_user

# Кэш в процессе: tg_id -> message_id корневого сообщения
_ROOT_IDS: Dict[int, int] = {}

def _get_cached_root_id(tg_id: int) -> Optional[int]:
    return _ROOT_IDS.get(tg_id)

def _cache_root_id(tg_id: int, msg_id: int) -> None:
    _ROOT_IDS[tg_id] = msg_id

async def ensure_root(
    message: Message,
    text: str = "Загрузка…",
    reply_markup: Optional[InlineKeyboardMarkup] = None,
    parse_mode: Optional[str] = "HTML",
) -> int:
    """
    Гарантирует одно корневое сообщение бота (переживает рестарты).
    1) Пытаемся редактировать существующее (из RAM или БД).
    2) Если не вышло — создаём новое и сохраняем в БД.
    """
    bot: Bot = message.bot
    tg_id = message.from_user.id
    chat_id = message.chat.id

    msg_id = _get_cached_root_id(tg_id)
    if not msg_id:
        u = get_user(tg_id)
        if u and u["root_message_id"]:
            msg_id = int(u["root_message_id"])
            _cache_root_id(tg_id, msg_id)

    if msg_id:
        try:
            await bot.edit_message_text(
                chat_id=chat_id,
                message_id=msg_id,
                text=text,
                reply_markup=reply_markup,
                parse_mode=parse_mode,
            )
            return msg_id
        except TelegramBadRequest as e:
            s = str(e).lower()
            if "message is not modified" in s:
                return msg_id
            # если "not found" или "can't be edited" — создадим новое ниже
            msg_id = None

    root = await bot.send_message(
        chat_id=chat_id,
        text=text,
        reply_markup=reply_markup,
        parse_mode=parse_mode,
    )
    _cache_root_id(tg_id, root.message_id)
    upsert_user(tg_id, root_message_id=root.message_id)
    return root.message_id

async def render(
    message: Message,
    text: str,
    reply_markup: Optional[InlineKeyboardMarkup] = None,
    parse_mode: Optional[str] = "HTML",
) -> None:
    """
    Редактирует одно корневое сообщение. Если потеряно — создаёт заново.
    """
    await ensure_root(message, "Загрузка…")
    bot: Bot = message.bot
    tg_id = message.from_user.id
    chat_id = message.chat.id
    msg_id = _get_cached_root_id(tg_id)
    if msg_id is None:
        msg_id = await ensure_root(message, "Загрузка…")

    try:
        await bot.edit_message_text(
            chat_id=chat_id,
            message_id=msg_id,
            text=text,
            reply_markup=reply_markup,
            parse_mode=parse_mode,
        )
    except TelegramBadRequest as e:
        s = str(e).lower()
        if "message to edit not found" in s or "message can't be edited" in s:
            new_id = await ensure_root(message, text, reply_markup, parse_mode)
            _cache_root_id(tg_id, new_id)
            upsert_user(tg_id, root_message_id=new_id)
        elif "message is not modified" in s:
            pass
        else:
            raise

# ========================= УДОБНЫЕ АДАПТЕРЫ =========================

async def render_cb(
    callback: CallbackQuery,
    text: str,
    reply_markup: Optional[InlineKeyboardMarkup] = None,
    parse_mode: Optional[str] = "HTML",
    show_ok: bool = False,
) -> None:
    """
    Рендер из CallbackQuery в то же корневое сообщение.
    """
    if callback.message is None:
        return
    try:
        await callback.answer("Готово" if show_ok else None)
    except Exception:
        pass
    await render(callback.message, text, reply_markup=reply_markup, parse_mode=parse_mode)

Event = Union[Message, CallbackQuery]

async def render_event(
    event: Event,
    text: str,
    reply_markup: Optional[InlineKeyboardMarkup] = None,
    parse_mode: Optional[str] = "HTML",
) -> None:
    """
    Универсальный рендер: принимает либо Message, либо CallbackQuery.
    """
    if isinstance(event, CallbackQuery):
        await render_cb(event, text, reply_markup=reply_markup, parse_mode=parse_mode)
    else:
        await render(event, text, reply_markup=reply_markup, parse_mode=parse_mode)
