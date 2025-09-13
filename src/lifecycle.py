from typing import Dict
from aiogram import Bot
from aiogram.types import ReplyKeyboardRemove
from .config import DOT
from .keyboards import reply_kb_share_contact

# tg_id -> message_id тех-сообщения
CONTACT_HELPERS: Dict[int, int] = {}

async def show_contact_keyboard_silent(bot: Bot, chat_id: int, tg_id: int):
    if tg_id in CONTACT_HELPERS:
        return
    kb = reply_kb_share_contact()
    msg = await bot.send_message(chat_id, DOT, reply_markup=kb, disable_notification=True)
    CONTACT_HELPERS[tg_id] = msg.message_id

async def hide_contact_keyboard(bot: Bot, chat_id: int, tg_id: int):
    mid = CONTACT_HELPERS.pop(tg_id, None)
    if mid is None:
        return
    try:
        rm = ReplyKeyboardRemove()
        m = await bot.send_message(chat_id, DOT, reply_markup=rm, disable_notification=True)
        # удалить тех-сообщение «remove» и исходное
        await safe_delete(bot, chat_id, m.message_id)
    except Exception:
        pass
    await safe_delete(bot, chat_id, mid)

async def safe_delete(bot: Bot, chat_id: int, message_id: int):
    try:
        await bot.delete_message(chat_id, message_id)
    except Exception:
        pass

async def enforce_no_contact_keyboard(state: str, bot: Bot, chat_id: int, tg_id: int):
    if state not in ("ASK_PHONE", "CHANGE_PHONE") and tg_id in CONTACT_HELPERS:
        await hide_contact_keyboard(bot, chat_id, tg_id)
