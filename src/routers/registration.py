from __future__ import annotations

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery

from ..services.root_message import render, render_event
from ..states import (
    S_WELCOME,
    S_ASK_NAME,
    S_ASK_PHONE,
    S_MENU,
    S_SETTINGS,
    S_CHANGE_PHONE,
    WELCOME_TEXT,
    ASK_NAME_TEXT,
    ASK_PHONE_TEXT,
    REG_OK_TEXT,
    SETTINGS_TEXT,
    CHANGE_PHONE_TEXT,
    PLACEHOLDER_TEXT,
    esc,
)
from ..keyboards import kb_welcome, kb_back, kb_menu, kb_settings, kb_back_to_settings
from ..db import get_user, upsert_user, log_action, normalize_phone, init_db

router = Router(name="registration")


def _valid_name(name: str) -> bool:
    name = (name or "").strip()
    return 2 <= len(name) <= 64


def _is_registered(user) -> bool:
    return bool(user and user["phone"])


# ───────────────────────────── Навигация «Назад» ──────────────────────────────

@router.callback_query(F.data.startswith("back:"))
async def nav_back(cb: CallbackQuery) -> None:
    tg_id = cb.from_user.id
    target = cb.data.split(":", 1)[1]
    user = get_user(tg_id)

    # Если уже зарегистрирован — любые «назад» можно безопасно вести в меню
    if _is_registered(user) and target in {"WELCOME", "ASK_NAME"}:
        upsert_user(tg_id, state=S_MENU)
        await render_event(cb, "Главное меню", reply_markup=kb_menu())
        try: await cb.answer()
        except Exception: pass
        return

    if target == "WELCOME":
        upsert_user(tg_id, state=S_WELCOME)
        await render_event(cb, WELCOME_TEXT(), reply_markup=kb_welcome())

    elif target == "ASK_NAME":
        upsert_user(tg_id, state=S_ASK_NAME)
        await render_event(cb, ASK_NAME_TEXT, reply_markup=kb_back("WELCOME"))

    elif target == "MENU":
        upsert_user(tg_id, state=S_MENU)
        await render_event(cb, "Главное меню", reply_markup=kb_menu())

    elif target == "SETTINGS":
        upsert_user(tg_id, state=S_SETTINGS)
        u = get_user(tg_id)
        await render_event(cb, SETTINGS_TEXT(u["name"], u["phone"]), reply_markup=kb_settings())

    try:
        await cb.answer()
    except Exception:
        pass


# ─────────────────────────── Прогресс регистрации ────────────────────────────

@router.callback_query(F.data == "continue")
async def cb_continue(cb: CallbackQuery) -> None:
    tg_id = cb.from_user.id
    user = get_user(tg_id)

    # Если уже зарегистрирован — сразу в меню
    if _is_registered(user):
        upsert_user(tg_id, state=S_MENU)
        await render_event(cb, "Главное меню", reply_markup=kb_menu())
        try: await cb.answer()
        except Exception: pass
        return

    upsert_user(tg_id, state=S_ASK_NAME)
    await render_event(cb, ASK_NAME_TEXT, reply_markup=kb_back("WELCOME"))
    try:
        await cb.answer()
    except Exception:
        pass


@router.callback_query(F.data == "settings")
async def cb_settings(cb: CallbackQuery) -> None:
    tg_id = cb.from_user.id
    upsert_user(tg_id, state=S_SETTINGS)
    u = get_user(tg_id)
    await render_event(cb, SETTINGS_TEXT(u["name"], u["phone"]), reply_markup=kb_settings())
    try:
        await cb.answer()
    except Exception:
        pass


@router.callback_query(F.data == "change_phone")
async def cb_change_phone(cb: CallbackQuery) -> None:
    tg_id = cb.from_user.id
    upsert_user(tg_id, state=S_CHANGE_PHONE)
    await render_event(cb, CHANGE_PHONE_TEXT, reply_markup=kb_back_to_settings())
    try:
        await cb.answer()
    except Exception:
        pass


# ─────────── Прочие пункты главного меню (временно-заглушки) ────────────

@router.callback_query(F.data == "send_admin")
async def cb_send_admin(cb: CallbackQuery) -> None:
    await render_event(cb, PLACEHOLDER_TEXT, reply_markup=kb_back("MENU"))
    try:
        await cb.answer("Скоро будет доступно", show_alert=False)
    except Exception:
        pass


@router.callback_query(F.data == "tournament")
async def cb_tournament(cb: CallbackQuery) -> None:
    await render_event(cb, PLACEHOLDER_TEXT, reply_markup=kb_back("MENU"))
    try:
        await cb.answer("Скоро будет доступно", show_alert=False)
    except Exception:
        pass


@router.callback_query(F.data == "actions")
async def cb_actions(cb: CallbackQuery) -> None:
    await render_event(cb, PLACEHOLDER_TEXT, reply_markup=kb_back("MENU"))
    try:
        await cb.answer("Скоро будет доступно", show_alert=False)
    except Exception:
        pass


# ───────────────────────── Ввод имени / телефона ─────────────────────────────

@router.message(F.content_type == "text")
async def on_text(m: Message) -> None:
    init_db()
    tg_id = m.from_user.id

    # режим «одно сообщение»: удаляем пользовательский текст
    try:
        await m.delete()
    except Exception:
        pass

    user = get_user(tg_id)
    if user is None:
        upsert_user(tg_id, state=S_WELCOME)
        user = get_user(tg_id)
    state = user["state"]

    # Если уже зарегистрирован — любой текст кидает в меню
    if _is_registered(user) and state in {S_WELCOME, S_ASK_NAME, S_ASK_PHONE}:
        upsert_user(tg_id, state=S_MENU)
        await render(m, "Главное меню", reply_markup=kb_menu())
        return

    if state == S_ASK_NAME:
        name = (m.text or "").strip()
        if not _valid_name(name):
            await render(
                m,
                "Имя слишком короткое/длинное. Введи от 2 до 64 символов.\n\n" + ASK_NAME_TEXT,
                reply_markup=kb_back("WELCOME"),
            )
        else:
            upsert_user(tg_id, name=name, state=S_ASK_PHONE)
            await render(
                m,
                ASK_PHONE_TEXT + "\n\n<i>Пришли номер в формате: +7 999 123-45-67 или 89991234567</i>",
                reply_markup=kb_back("ASK_NAME"),
            )
            log_action(tg_id, "set_name", name)
        return

    if state in (S_ASK_PHONE, S_CHANGE_PHONE):
        phone_val = normalize_phone(m.text or "")
        if not phone_val:
            back_target = "ASK_NAME" if state == S_ASK_PHONE else "SETTINGS"
            msg = ASK_PHONE_TEXT if state == S_ASK_PHONE else CHANGE_PHONE_TEXT
            await render(
                m,
                "Не получилось распознать номер. Проверь формат и попробуй снова.\n\n" + msg,
                reply_markup=kb_back(back_target),
            )
            return

        upsert_user(tg_id, phone=phone_val)

        if state == S_ASK_PHONE:
            upsert_user(tg_id, state=S_MENU)
            u = get_user(tg_id)
            await render(m, REG_OK_TEXT(u["name"], u["phone"]), reply_markup=kb_menu())
            log_action(tg_id, "set_phone", phone_val)
        else:
            upsert_user(tg_id, state=S_SETTINGS)
            u = get_user(tg_id)
            await render(
                m,
                f"Готово! ✅ Телефон обновлён: <b>{esc(u['phone'])}</b>",
                reply_markup=kb_settings(),
            )
            log_action(tg_id, "change_phone", phone_val)
        return

    # Всё остальное → главное меню
    upsert_user(tg_id, state=S_MENU)
    await render(m, "Главное меню", reply_markup=kb_menu())


# ────────────────────────── Catch-all для callback ────────────────────────────

@router.callback_query()
async def _fallback_cb(cb: CallbackQuery) -> None:
    try:
        await cb.answer("Кнопка ещё не привязана. Возвращаю в меню.", show_alert=False)
    except Exception:
        pass
    await render_event(cb, "Главное меню", reply_markup=kb_menu())
