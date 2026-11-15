"""Inicia el frontend público y la API interna en el mismo contenedor."""
import os
from pathlib import Path
import signal
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
WEB = ROOT / "web"


def main() -> int:
    if not (os.getenv("SUPABASE_DB_URL") or os.getenv("DATABASE_URL")):
        raise SystemExit("Configura SUPABASE_DB_URL para conectar la base existente.")
    if len(os.getenv("HUMBERTITO_SESSION_SECRET", "")) < 32:
        raise SystemExit("Configura HUMBERTITO_SESSION_SECRET con al menos 32 caracteres.")

    stopping = False

    def stop(_signum, _frame):
        nonlocal stopping
        stopping = True

    signal.signal(signal.SIGTERM, stop)
    signal.signal(signal.SIGINT, stop)
    children: list[subprocess.Popen] = []
    try:
        children.append(subprocess.Popen([
            sys.executable, "-m", "uvicorn", "backend.api:create_app",
            "--factory", "--host", "127.0.0.1", "--port", "8000",
        ], cwd=ROOT))
        children.append(subprocess.Popen([
            "node", "node_modules/next/dist/bin/next", "start",
            "--hostname", "0.0.0.0", "--port", os.getenv("PORT", "3000"),
        ], cwd=WEB))
        while not stopping:
            for child in children:
                code = child.poll()
                if code is not None:
                    return code if code > 0 else 1
            time.sleep(.25)
        return 0
    finally:
        for child in children:
            if child.poll() is None:
                child.terminate()
        for child in children:
            try:
                child.wait(timeout=8)
            except subprocess.TimeoutExpired:
                child.kill()
                child.wait()


if __name__ == "__main__":
    raise SystemExit(main())
