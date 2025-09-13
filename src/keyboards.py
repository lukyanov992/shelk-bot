from __future__ import annotations
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from .states import CHANNEL_URL

def kb_welcome() -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Продолжить", callback_data="continue")]
    ])
    return kb

def kb_back(to: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ Назад", callback_data=f"back:{to}")]
    ])

def kb_menu() -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(text="📨 Отправить номер администратору", callback_data="send_admin")],
        [InlineKeyboardButton(text="🏆 Регистрация на турнир", callback_data="tournament")],
        [InlineKeyboardButton(text="🎁 Акции", callback_data="actions")],
    ]
    if CHANNEL_URL:
        rows.append([InlineKeyboardButton(text="➡️ Перейти в канал", url=CHANNEL_URL)])
    rows.append([InlineKeyboardButton(text="⚙️ Настройки", callback_data="settings")])
    return InlineKeyboardMarkup(inline_keyboard=rows)

def kb_settings() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📞 Изменить номер телефона", callback_data="change_phone")],
        [InlineKeyboardButton(text="⬅️ Назад в меню", callback_data="back:MENU")],
    ])

def kb_back_to_settings() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="back:SETTINGS")]
    ])
