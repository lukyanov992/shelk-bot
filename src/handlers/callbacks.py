from aiogram import Router
from aiogram.types import CallbackQuery
from ..db import get_user, upsert_user, log_action
from ..root_message import ensure_root_message, edit_root
from ..texts import (
    WELCOME_TEXT, ASK_NAME_TEXT, ASK_PHONE_TEXT, SETTINGS_TEXT,
    MENU_TEXT, PLACEHOLDER_TEXT
)
from ..keyboards import kb_welcome, kb_back, kb_menu, kb_settings, kb_back_to_settings
from ..states import S_WELCOME, S_ASK_NAME, S_MENU, S_SETTINGS, S_CHANGE_PHONE, S_ASK_PHONE
from ..lifecycle import enforce_no_contact_keyboard, show_contact_keyboard_silent

router = Router()

@router.callback_query()
async def on_cb(c: CallbackQuery):
    tg_id = c.from_user.id
    user = get_user(tg_id)
    msg_id = await ensure_root_message(c.bot, tg_id, c.message.chat.id)
    data = c.data or ""

    if data.startswith("back:"):
        target = data.split(":", 1)[1]
        if target == "WELCOME":
            upsert_user(tg_id, state=S_WELCOME)
            await enforce_no_contact_keyboard(S_WELCOME, c.bot, c.message.chat.id, tg_id)
            await edit_root(c.bot, c.message.chat.id, msg_id, WELCOME_TEXT(), kb_welcome())
        elif target == "ASK_NAME":
            upsert_user(tg_id, state=S_ASK_NAME)
            await enforce_no_contact_keyboard(S_ASK_NAME, c.bot, c.message.chat.id, tg_id)
            await edit_root(c.bot, c.message.chat.id, msg_id, ASK_NAME_TEXT, kb_back("WELCOME"))
        elif target == "MENU":
            upsert_user(tg_id, state=S_MENU)
            await enforce_no_contact_keyboard(S_MENU, c.bot, c.message.chat.id, tg_id)
            from ..config import CHANNEL_URL
            await edit_root(c.bot, c.message.chat.id, msg_id, MENU_TEXT, kb_menu(CHANNEL_URL))
        elif target == "SETTINGS":
            upsert_user(tg_id, state=S_SETTINGS)
            await enforce_no_contact_keyboard(S_SETTINGS, c.bot, c.message.chat.id, tg_id)
            user = get_user(tg_id)
            await edit_root(c.bot, c.message.chat.id, msg_id, SETTINGS_TEXT(user["name"], user["phone"]), kb_settings())
        await c.answer()
        return

    if data == "continue":
        upsert_user(tg_id, state=S_ASK_NAME)
        await enforce_no_contact_keyboard(S_ASK_NAME, c.bot, c.message.chat.id, tg_id)
        await edit_root(c.bot, c.message.chat.id, msg_id, ASK_NAME_TEXT, kb_back("WELCOME"))
        await c.answer()
        return

    if data == "menu":
        upsert_user(tg_id, state=S_MENU)
        await enforce_no_contact_keyboard(S_MENU, c.bot, c.message.chat.id, tg_id)
        from ..config import CHANNEL_URL
        await edit_root(c.bot, c.message.chat.id, msg_id, MENU_TEXT, kb_menu(CHANNEL_URL))
        await c.answer()
        return

    if data == "settings":
        upsert_user(tg_id, state=S_SETTINGS)
        await enforce_no_contact_keyboard(S_SETTINGS, c.bot, c.message.chat.id, tg_id)
        user = get_user(tg_id)
        await edit_root(c.bot, c.message.chat.id, msg_id, SETTINGS_TEXT(user["name"], user["phone"]), kb_settings())
        await c.answer()
        return

    if data == "change_phone":
        upsert_user(tg_id, state=S_CHANGE_PHONE)
        await edit_root(c.bot, c.message.chat.id, msg_id, "Введи новый номер телефона или отправь контакт.\n\nПримеры: <code>+7 999 123-45-67</code>, <code>89991234567</code>", kb_back_to_settings())
        await show_contact_keyboard_silent(c.bot, c.message.chat.id, tg_id)
        await c.answer()
        return

    if data in ("send_admin", "tournament", "actions"):
        upsert_user(tg_id, state=S_MENU)
        await enforce_no_contact_keyboard(S_MENU, c.bot, c.message.chat.id, tg_id)
        await edit_root(c.bot, c.message.chat.id, msg_id, PLACEHOLDER_TEXT, kb_back("MENU"))
        await c.answer("Раздел скоро будет доступен")
        return

    await c.answer()
