from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import InlineKeyboardMarkup
from .db import get_user, upsert_user
from .texts import WELCOME_TEXT
from .keyboards import kb_welcome

async def ensure_root_message(bot: Bot, tg_id: int, chat_id: int) -> int:
    user = get_user(tg_id)
    if user is None or user["root_message_id"] is None:
        msg = await bot.send_message(chat_id, WELCOME_TEXT(), reply_markup=kb_welcome())
        upsert_user(tg_id, state="WELCOME", root_message_id=msg.message_id)
        user = get_user(tg_id)
        return msg.message_id
    return int(user["root_message_id"])

async def edit_root(bot: Bot, chat_id: int, message_id: int, text: str, reply_markup: InlineKeyboardMarkup):
    try:
        await bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=text,
            reply_markup=reply_markup
        )
    except TelegramBadRequest as e:
        emsg = str(e).lower()
        if "message to edit not found" in emsg:
            msg = await bot.send_message(chat_id, text, reply_markup=reply_markup)
            upsert_user(chat_id, root_message_id=msg.message_id)  # tg_id == chat_id в приватных
            return
        if "message is not modified" in emsg:
            return
        raise
