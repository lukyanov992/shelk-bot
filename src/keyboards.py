from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

def kb_welcome() -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="Продолжить", callback_data="continue")
    ]])
    return kb

def kb_back(to: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="⬅️ Назад", callback_data=f"back:{to}")
    ]])
    return kb

def kb_menu(channel_url: str | None = None) -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(text="📨 Отправить номер администратору", callback_data="send_admin")],
        [InlineKeyboardButton(text="🏆 Регистрация на турнир", callback_data="tournament")],
        [InlineKeyboardButton(text="🎁 Акции", callback_data="actions")],
    ]
    if channel_url:
        rows.append([InlineKeyboardButton(text="➡️ Перейти в канал", url=channel_url)])
    rows.append([InlineKeyboardButton(text="⚙️ Настройки", callback_data="settings")])
    return InlineKeyboardMarkup(inline_keyboard=rows)

def kb_settings() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="📞 Изменить номер телефона", callback_data="change_phone")
    ],[
        InlineKeyboardButton(text="⬅️ Назад в меню", callback_data="back:MENU")
    ]])

def kb_back_to_settings() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="⬅️ Назад", callback_data="back:SETTINGS")
    ]])

def reply_kb_share_contact() -> ReplyKeyboardMarkup:
    rb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, keyboard=[[
        KeyboardButton(text="📱 Поделиться номером", request_contact=True)
    ]])
    return rb
