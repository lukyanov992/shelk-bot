import sqlite3
from typing import Optional
from .config import DB_PATH
from .utils import now_iso

def db() -> sqlite3.Connection:
    con = sqlite3.connect(str(DB_PATH), check_same_thread=False)
    con.row_factory = sqlite3.Row
    return con

def init_db():
    con = db()
    c = con.cursor()
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
    )
    """)
    c.execute("""
    CREATE TABLE IF NOT EXISTS audit (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tg_id INTEGER NOT NULL,
        action TEXT NOT NULL,
        meta TEXT,
        created_at TEXT NOT NULL
    )
    """)
    con.commit()
    con.close()

def get_user(tg_id: int) -> Optional[sqlite3.Row]:
    con = db()
    c = con.cursor()
    c.execute("SELECT * FROM users WHERE tg_id = ?", (tg_id,))
    row = c.fetchone()
    con.close()
    return row

def upsert_user(tg_id: int, **fields):
    con = db()
    c = con.cursor()
    cur = get_user(tg_id)
    if cur is None:
        cols = ["tg_id", "created_at", "updated_at"] + list(fields.keys())
        vals = [tg_id, now_iso(), now_iso()] + list(fields.values())
        placeholders = ",".join(["?"] * len(vals))
        c.execute(f"INSERT INTO users ({','.join(cols)}) VALUES ({placeholders})", vals)
    else:
        sets = [f"{k} = ?" for k in fields.keys()]
        vals = list(fields.values())
        sets.append("updated_at = ?")
        vals.append(now_iso())
        vals.append(tg_id)
        c.execute(f"UPDATE users SET {', '.join(sets)} WHERE tg_id = ?", vals)
    con.commit()
    con.close()

def log_action(tg_id: int, action: str, meta: str = ""):
    con = db()
    c = con.cursor()
    c.execute("INSERT INTO audit (tg_id, action, meta, created_at) VALUES (?,?,?,?)",
              (tg_id, action, meta, now_iso()))
    con.commit()
    con.close()

def normalize_phone(text: str | None) -> str | None:
    import re
    if not text:
        return None
    digits = re.sub(r"[^\d+]", "", text)
    only = re.sub(r"\D", "", digits)
    if len(only) < 10:
        return None
    if only.startswith("8") and len(only) == 11:
        return "+7" + only[1:]
    if digits.startswith("+") and len(only) >= 10:
        return "+" + only
    if len(only) >= 10:
        return only
    return None
