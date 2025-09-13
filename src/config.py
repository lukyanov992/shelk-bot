from pathlib import Path
import os
from dotenv import load_dotenv
import re

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DOTENV_PATH = PROJECT_ROOT / ".env"
load_dotenv(dotenv_path=DOTENV_PATH, override=True)

BOT_TOKEN = (os.getenv("BOT_TOKEN") or "").strip()
PRIVACY_URL = (os.getenv("PRIVACY_URL") or "https://example.com/privacy").strip()
CHANNEL_URL = (os.getenv("CHANNEL_URL") or "").strip()
DISABLE_SINGLE_INSTANCE = (os.getenv("DISABLE_SINGLE_INSTANCE") or "0").strip() == "1"

TOKEN_RE = re.compile(r"^\d{6,}:[A-Za-z0-9_-]{30,}$")
if not TOKEN_RE.match(BOT_TOKEN):
    mask = BOT_TOKEN[:6] + "..." if BOT_TOKEN else "<empty>"
    raise SystemExit(
        "❌ BOT_TOKEN некорректен или не загружен.\n"
        f"   Загружено из: {DOTENV_PATH}\n"
        f"   Текущее значение: {mask}\n"
        "   Проверь .env (без кавычек и пробелов) или получи новый токен у @BotFather."
    )

DOT = "·"
DB_PATH = PROJECT_ROOT / "colizeum_bot.sqlite3"
LOCK_PATH = PROJECT_ROOT / "colizeum_bot.lock"
