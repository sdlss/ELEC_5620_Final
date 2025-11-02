"""
CLI: Create an app_user row with a bcrypt-hashed password.

Usage (Windows cmd.exe):
    conda run -p d:\\Desktop\\ELEC_5620_Final\\.conda python -m backend.create_user --email you@example.com --password YourPass123 --role consumer

Assumptions:
- DATABASE_URL is set in environment or in backend/.env
- Schema from final5620.sql already applied (table app_user exists)
"""
from __future__ import annotations
import os
import sys
import argparse
from typing import Optional
from dotenv import load_dotenv

# Ensure .env is loaded: use backend/.env as authoritative
HERE = os.path.dirname(os.path.abspath(__file__))
try:
    load_dotenv(os.path.join(HERE, ".env"), override=True)
except Exception:
    pass
try:
    load_dotenv(override=False)  # root .env (do not override backend/.env)
except Exception:
    pass

try:
    import bcrypt  # type: ignore
except Exception as e:
    print("[create_user] bcrypt is not installed. Install backend requirements first.", file=sys.stderr)
    sys.exit(2)

# Import DB session and models lazily to avoid side effects on import
try:
    from .case.database import SessionLocal  # type: ignore
    from .case import models as case_models  # type: ignore
except Exception:
    # Fallback for direct execution as module/script
    from case.database import SessionLocal  # type: ignore
    from case import models as case_models  # type: ignore


def create_user(email: str, password: str, role: str = "consumer") -> Optional[int]:
    email = (email or "").strip()
    if not email or "@" not in email:
        print("[create_user] invalid email", file=sys.stderr)
        return 1
    password = (password or "").strip()
    if not password:
        print("[create_user] password is required", file=sys.stderr)
        return 1
    if not role:
        role = "consumer"

    db = SessionLocal()
    try:
        # Check if exists
        existing = db.query(case_models.AppUser).filter(case_models.AppUser.email == email).first()
        if existing:
            print(f"[create_user] user already exists: {email}")
            return 0
        pw_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
        user = case_models.AppUser(email=email, password_hash=pw_hash, role=role)
        db.add(user)
        db.commit()
        try:
            db.refresh(user)
        except Exception:
            pass
        print(f"[create_user] created user id={getattr(user, 'id', None)} email={email} role={role}")
        return 0
    finally:
        try:
            db.close()
        except Exception:
            pass


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Create an app user (bcrypt-hashed password)")
    parser.add_argument("--email", required=True, help="Email for the user")
    parser.add_argument("--password", required=True, help="Plaintext password; will be hashed with bcrypt")
    parser.add_argument("--role", default="consumer", help="Role (default: consumer)")
    args = parser.parse_args(argv)
    return create_user(args.email, args.password, args.role) or 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
