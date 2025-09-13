from __future__ import annotations
import os, re, json, sqlite3
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DB_PATH = PROJECT_ROOT / "colizeum_bot.sqlite3"

def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")

def db() -> sqlite3.Connection:
    con = sqlite3.connect(str(DB_PATH), check_same_thread=False)
    con.row_factory = sqlite3.Row
    return con

def init_db() -> None:
    con = db(); c = con.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tg_id INTEGER UNIQUE NOT NULL,
        name TEXT,
        phone TEXT,
        state TEXT NOT NULL DEFAULT 'WELCOME',
        root_message_id INTEGER,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
    )""")
    c.execute("""
    CREATE TABLE IF NOT EXISTS audit (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tg_id INTEGER NOT NULL,
        action TEXT NOT NULL,
        meta TEXT,
        created_at TEXT NOT NULL
    )""")
    con.commit(); con.close()

def get_user(tg_id: int) -> Optional[sqlite3.Row]:
    con = db(); c = con.cursor()
    c.execute("SELECT * FROM users WHERE tg_id = ?", (tg_id,))
    row = c.fetchone(); con.close()
    return row

def upsert_user(tg_id: int, **fields):
    con = db(); c = con.cursor()
    cur = get_user(tg_id)
    # фильтруем неизвестные поля на случай опечаток
    allowed = {"tg_id","name","phone","state","root_message_id","created_at","updated_at"}
    clean_fields = {k:v for k,v in fields.items() if k in allowed}

    if cur is None:
        cols = ["tg_id","created_at","updated_at"] + list(clean_fields.keys())
        vals = [tg_id, now_iso(), now_iso()] + list(clean_fields.values())
        c.execute(f"INSERT INTO users ({','.join(cols)}) VALUES ({','.join(['?']*len(vals))})", vals)
    else:
        sets = [f"{k}=?" for k in clean_fields]
        vals = list(clean_fields.values())
        sets.append("updated_at=?"); vals.append(now_iso()); vals.append(tg_id)
        c.execute(f"UPDATE users SET {', '.join(sets)} WHERE tg_id = ?", vals)
    con.commit(); con.close()


def log_action(tg_id: int, action: str, meta: str = ""):
    con = db(); c = con.cursor()
    c.execute("INSERT INTO audit (tg_id, action, meta, created_at) VALUES (?,?,?,?)",
              (tg_id, action, meta, now_iso()))
    con.commit(); con.close()

def normalize_phone(text: Optional[str]) -> Optional[str]:
    if not text: return None
    digits = re.sub(r"[^\d+]", "", text)
    only = re.sub(r"\D", "", digits)
    if len(only) < 10: return None
    if only.startswith("8") and len(only)==11: return "+7"+only[1:]
    if digits.startswith("+") and len(only)>=10: return "+"+only
    if len(only) >= 10: return only
    return None
