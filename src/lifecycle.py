from __future__ import annotations

import asyncio
from typing import Dict

from aiogram import Bot
from aiogram.types import ReplyKeyboardRemove

from .config import DOT
from .keyboards import reply_kb_share_contact

# tg_id -> message_id немого тех-сообщения с реплай-кнопкой
CONTACT_HELPERS: Dict[int, int] = {}

# Пер-пользовательские локи на операции с реплай-клавиатурой,
# чтобы не было двойных "DOT"-сообщений при гонках.
_CONTACT_LOCKS: Dict[int, asyncio.Lock] = {}

def _contact_lock_for(tg_id: int) -> asyncio.Lock:
    lk = _CONTACT_LOCKS.get(tg_id)
    if lk is None:
        lk = asyncio.Lock()
        _CONTACT_LOCKS[tg_id] = lk
    return lk


async def safe_delete(bot: Bot, chat_id: int, message_id: int):
    try:
        await bot.delete_message(chat_id, message_id)
    except Exception:
        pass


async def show_contact_keyboard_silent(bot: Bot, chat_id: int, tg_id: int):
    """
    Идемпотентно показывает реплай-кнопку «📱 Поделиться номером»,
    прикрепляя её к тихому DOT-сообщению. Защищено локом.
    """
    lock = _contact_lock_for(tg_id)
    async with lock:
        if tg_id in CONTACT_HELPERS:
            return
        kb = reply_kb_share_contact()
        msg = await bot.send_message(chat_id, DOT, reply_markup=kb, disable_notification=True)
        CONTACT_HELPERS[tg_id] = msg.message_id


async def hide_contact_keyboard(bot: Bot, chat_id: int, tg_id: int):
    """
    Идемпотентно скрывает клавиатуру, удаляя и вспомогательное DOT-сообщение,
    и временное "remove"-сообщение. Защищено локом.
    """
    lock = _contact_lock_for(tg_id)
    async with lock:
        mid = CONTACT_HELPERS.pop(tg_id, None)
        if mid is None:
            return
        try:
            rm = ReplyKeyboardRemove()
            m = await bot.send_message(chat_id, DOT, reply_markup=rm, disable_notification=True)
            await safe_delete(bot, chat_id, m.message_id)
        except Exception:
            pass
        await safe_delete(bot, chat_id, mid)


async def enforce_no_contact_keyboard(state: str, bot: Bot, chat_id: int, tg_id: int):
    """
    Во всех состояниях, кроме ASK_PHONE/CHANGE_PHONE, реплай-клавиатуры быть не должно.
    """
    if state not in ("ASK_PHONE", "CHANGE_PHONE") and tg_id in CONTACT_HELPERS:
        await hide_contact_keyboard(bot, chat_id, tg_id)
