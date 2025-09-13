from aiogram import Router, F
from aiogram.types import Message
from ..db import get_user, upsert_user, log_action, normalize_phone
from ..root_message import ensure_root_message, edit_root
from ..texts import (
    ASK_NAME_TEXT, ASK_PHONE_TEXT, REG_OK_TEXT, MENU_TEXT
)
from ..keyboards import kb_back, kb_menu, kb_settings, kb_back_to_settings
from ..states import S_ASK_NAME, S_ASK_PHONE, S_MENU, S_SETTINGS, S_CHANGE_PHONE
from ..lifecycle import enforce_no_contact_keyboard, show_contact_keyboard_silent, hide_contact_keyboard, safe_delete
from ..config import CHANNEL_URL

router = Router()

def _valid_name(name: str) -> bool:
    name = (name or "").strip()
    return 2 <= len(name) <= 64

@router.message(F.content_type.in_({"text", "contact"}))
async def handle_text_or_contact(m: Message):
    tg_id = m.from_user.id
    user = get_user(tg_id)
    msg_id = await ensure_root_message(m.bot, tg_id, m.chat.id)
    state = user["state"] if user else S_MENU

    # «одно сообщение»: удаляем любые тексты юзера
    if m.content_type == "text":
        await safe_delete(m.bot, m.chat.id, m.message_id)

    # имя
    if state == S_ASK_NAME and m.content_type == "text":
        name = (m.text or "").strip()
        if not _valid_name(name):
            await enforce_no_contact_keyboard(S_ASK_NAME, m.bot, m.chat.id, tg_id)
            await edit_root(m.bot, m.chat.id, msg_id,
                            "Имя слишком короткое/длинное. Введи от 2 до 64 символов.\n\n" + ASK_NAME_TEXT,
                            kb_back("WELCOME"))
            return
        upsert_user(tg_id, name=name, state=S_ASK_PHONE)
        await edit_root(m.bot, m.chat.id, msg_id, ASK_PHONE_TEXT, kb_back("ASK_NAME"))
        await show_contact_keyboard_silent(m.bot, m.chat.id, tg_id)
        log_action(tg_id, "set_name", name)
        return

    # телефон
    if state in (S_ASK_PHONE, S_CHANGE_PHONE):
        phone_val = None
        if m.content_type == "contact" and getattr(m, "contact", None) and m.contact.phone_number:
            phone_val = normalize_phone(m.contact.phone_number)
        elif m.content_type == "text":
            phone_val = normalize_phone(m.text)

        if m.content_type == "contact":
            await safe_delete(m.bot, m.chat.id, m.message_id)

        if not phone_val:
            back_target = "ASK_NAME" if state == S_ASK_PHONE else "SETTINGS"
            await edit_root(m.bot, m.chat.id, msg_id,
                            "Не получилось распознать номер. Проверь формат и попробуй снова.\n\n"
                            + (ASK_PHONE_TEXT if state == S_ASK_PHONE else "Введи новый номер телефона или отправь контакт.\n\nПримеры: <code>+7 999 123-45-67</code>, <code>89991234567</code>"),
                            kb_back(back_target))
            return

        upsert_user(tg_id, phone=phone_val)
        await hide_contact_keyboard(m.bot, m.chat.id, tg_id)

        if state == S_ASK_PHONE:
            upsert_user(tg_id, state=S_MENU)
            u = get_user(tg_id)
            await edit_root(m.bot, m.chat.id, msg_id, REG_OK_TEXT(u["name"], u["phone"]), kb_menu(CHANNEL_URL))
            log_action(tg_id, "set_phone", phone_val)
            return
        else:
            upsert_user(tg_id, state=S_SETTINGS)
            u = get_user(tg_id)
            from ..texts import esc
            await edit_root(m.bot, m.chat.id, msg_id,
                            f"Готово! ✅ Телефон обновлён: <b>{esc(u['phone'])}</b>",
                            kb_settings())
            log_action(tg_id, "change_phone", phone_val)
            return

    # Иное — вернуть в меню и скрыть клавиатуру на всякий
    await enforce_no_contact_keyboard(S_MENU, m.bot, m.chat.id, tg_id)
    upsert_user(tg_id, state=S_MENU)
    await edit_root(m.bot, m.chat.id, msg_id, MENU_TEXT, kb_menu(CHANNEL_URL))
