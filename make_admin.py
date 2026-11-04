# Promote (or demote) a user. Run this on YOUR machine; there is deliberately no API for it,
# so nobody can make themselves admin through the website.
#
#   python make_admin.py yourusername            -> make admin
#   python make_admin.py yourusername --remove   -> back to normal user
import sys
from config.db import SessionLocal
from schemas.art_model import User


def set_role(username: str, role: str) -> bool:
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.username == username).first()
        if not user:
            return False
        user.role = role
        db.commit()
        return True
    finally:
        db.close()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit("Usage: python make_admin.py <username> [--remove]")
    role = "user" if "--remove" in sys.argv else "admin"
    if set_role(sys.argv[1], role):
        print(f"'{sys.argv[1]}' is now: {role}")
    else:
        sys.exit(f"No user named '{sys.argv[1]}'. Register first via /auth/register.")
