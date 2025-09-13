from __future__ import annotations
import os

S_WELCOME = "WELCOME"
S_ASK_NAME = "ASK_NAME"
S_ASK_PHONE = "ASK_PHONE"
S_MENU = "MENU"
S_SETTINGS = "SETTINGS"
S_CHANGE_PHONE = "CHANGE_PHONE"

PRIVACY_URL = (os.getenv("PRIVACY_URL") or "https://example.com/privacy").strip()
CHANNEL_URL  = (os.getenv("CHANNEL_URL")  or "").strip()

def esc(s: str | None) -> str:
    s = s or ""
    return s.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")

def WELCOME_TEXT() -> str:
    return (
        "Добро пожаловать в <b>Colizeum Щёлковский</b>! 💜\n\n"
        f"Используя этого бота, ты соглашаешься на обработку персональных данных. "
        f"Подробнее: <a href=\"{PRIVACY_URL}\">Политика конфиденциальности</a>.\n\n"
        "Для использования бота необходимо зарегистрироваться.\n"
        "Хорошей игры! 🎮🔥"
    )

ASK_NAME_TEXT = "Как тебя зовут?\n\n<i>Можно просто имя или ник, 2–64 символа.</i>"
ASK_PHONE_TEXT = (
    "Теперь напиши или отправь контакт с номером телефона, "
    "на который у тебя привязан аккаунт в клубе.\n\n"
    "Примеры: <code>+7 999 123-45-67</code>, <code>89991234567</code>"
)
def REG_OK_TEXT(name: str|None, phone: str|None) -> str:
    return (f"Готово! ✅\n\n<b>Имя:</b> {esc(name)}\n<b>Телефон:</b> {esc(phone)}\n\n"
            "Можешь пользоваться меню ниже.")
MENU_TEXT = "Главное меню"
def SETTINGS_TEXT(name: str|None, phone: str|None) -> str:
    return ("⚙️ <b>Настройки</b>\n\n"
            f"<b>Имя:</b> {esc(name) if name else '—'}\n"
            f"<b>Телефон:</b> {esc(phone) if phone else '—'}")
CHANGE_PHONE_TEXT = (
    "Введи новый номер телефона или отправь контакт.\n\n"
    "Примеры: <code>+7 999 123-45-67</code>, <code>89991234567</code>"
)
PLACEHOLDER_TEXT = "Раздел в разработке 🚧\n\nМы уже варим код в котле. Совсем скоро здесь всё заработает!"
