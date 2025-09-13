from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from ..db import get_user, upsert_user, log_action
from ..root_message import ensure_root_message, edit_root
from ..texts import WELCOME_TEXT, ASK_NAME_TEXT, SETTINGS_TEXT, MENU_TEXT
from ..keyboards import kb_welcome, kb_back, kb_menu, kb_settings
from ..states import S_WELCOME, S_ASK_NAME, S_MENU, S_SETTINGS
from ..lifecycle import enforce_no_contact_keyboard

router = Router()

@router.message(CommandStart())
async def handle_start(message: Message):
    tg_id = message.from_user.id
    user = get_user(tg_id)
    msg_id = await ensure_root_message(message.bot, tg_id, message.chat.id)
    await enforce_no_contact_keyboard(user["state"] if user else S_WELCOME, message.bot, message.chat.id, tg_id)
    await edit_root(message.bot, message.chat.id, msg_id, WELCOME_TEXT(), kb_welcome())
    log_action(tg_id, "start")
