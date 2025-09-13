from datetime import datetime, UTC
import json
import os
from .config import LOCK_PATH, DISABLE_SINGLE_INSTANCE

def now_iso() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds")

def _pid_alive(pid: int) -> bool:
    try:
        import psutil
        p = psutil.Process(pid)
        return p.is_running() and p.status() != psutil.STATUS_ZOMBIE
    except Exception:
        return False

def obtain_lock_or_exit():
    if DISABLE_SINGLE_INSTANCE:
        print("⚠️ Single-instance lock отключён (DISABLE_SINGLE_INSTANCE=1)")
        return
    if LOCK_PATH.exists():
        try:
            data = json.loads(LOCK_PATH.read_text(encoding="utf-8"))
            old_pid = int(data.get("pid") or 0)
        except Exception:
            old_pid = 0
        if old_pid and _pid_alive(old_pid):
            print(f"⚠️ Похоже, бот уже запущен (pid={old_pid}). Выход.")
            raise SystemExit(1)
        try:
            LOCK_PATH.unlink()
        except Exception:
            pass
    try:
        LOCK_PATH.write_text(json.dumps({"pid": os.getpid(), "started_at": now_iso()}), encoding="utf-8")
    except Exception as e:
        print(f"⚠️ Не удалось создать lock-файл: {e}")
