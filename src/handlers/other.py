from aiogram import Router, F
from aiogram.types import Message
from ..db import get_user, upsert_user
from ..root_message import ensure_root_message, edit_root
from ..texts import MENU_TEXT
from ..keyboards import kb_menu
from ..lifecycle import safe_delete, enforce_no_contact_keyboard
from ..states import S_MENU
from ..config import CHANNEL_URL

router = Router()

@router.message(F.content_type.in_({"photo", "sticker", "video", "document", "audio", "voice"}))
async def other(m: Message):
    tg_id = m.from_user.id
    user = get_user(tg_id)
    msg_id = await ensure_root_message(m.bot, tg_id, m.chat.id)
    await safe_delete(m.bot, m.chat.id, m.message_id)
    await enforce_no_contact_keyboard(S_MENU, m.bot, m.chat.id, tg_id)
    upsert_user(tg_id, state=S_MENU)
    await edit_root(m.bot, m.chat.id, msg_id, MENU_TEXT, kb_menu(CHANNEL_URL))
