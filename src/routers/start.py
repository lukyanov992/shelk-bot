from __future__ import annotations
from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from ..services.root_message import ensure_root, render
from ..db import init_db, get_user, upsert_user
from ..states import WELCOME_TEXT, S_WELCOME, S_MENU
from ..keyboards import kb_welcome, kb_menu

router = Router(name="start")

def _is_registered(user) -> bool:
    # считаем зарегистрированным, если есть телефон (как в твоей старой логике)
    return bool(user and user["phone"])

@router.message(CommandStart())
async def handle_start(message: Message) -> None:
    init_db()
    await ensure_root(message, "Загрузка…")

    tg_id = message.from_user.id
    user = get_user(tg_id)

    if _is_registered(user):
        # уже зарегистрирован → главное меню
        upsert_user(tg_id, state=S_MENU)
        await render(message, "Главное меню", reply_markup=kb_menu())
        return

    # не зарегистрирован → приветствие
    if user is None:
        upsert_user(tg_id, state=S_WELCOME)

    await render(message, WELCOME_TEXT(), reply_markup=kb_welcome())
