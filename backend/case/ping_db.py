r"""
Quick DB connectivity check for the case subsystem.

Usage (Windows cmd.exe examples):

1) Using existing environment variable
   set DATABASE_URL=postgresql://postgres:password@127.0.0.1:5432/final5620
   python -m backend.case.ping_db

2) Using conda run with a specific environment prefix
    D:\anaconda\Scripts\conda.exe run -p D:\Desktop\ELEC_5620_Final\.conda --no-capture-output python -m backend.case.ping_db

This script prints a simple SELECT 1 result and the server version.
It uses the same SQLAlchemy engine as backend.case.database.
"""

from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import text

# Load backend/.env as authoritative before importing engine so that DATABASE_URL is correct
try:
    backend_dir = Path(__file__).resolve().parents[1]
    backend_env = backend_dir / ".env"
    if backend_env.exists():
        load_dotenv(str(backend_env), override=True)
    # Optionally load root .env without overriding backend/.env
    load_dotenv(override=False)
except Exception:
    pass

from .database import engine, DB_URL  # reuse configuration


def main() -> int:
    try:
        print(f"Connecting to: {DB_URL}")
        with engine.connect() as conn:
            one = conn.execute(text("SELECT 1")).scalar()
            version = conn.execute(text("SELECT version()"))
            version_str = version.scalar() if version is not None else "<unknown>"
            print("SELECT 1 =>", one)
            print("Server version:", version_str)
        print("DB connectivity: OK")
        return 0
    except Exception as e:
        print("DB connectivity: FAILED")
        print("Error:", repr(e))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
