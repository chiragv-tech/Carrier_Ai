"""Authentication helpers using salted PBKDF2 password hashes."""
import hashlib
import hmac
import os
import re
from core import database

_ITERATIONS = 310_000

def hash_password(password: str) -> str:
    salt = os.urandom(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, _ITERATIONS)
    return f"pbkdf2_sha256${_ITERATIONS}${salt.hex()}${digest.hex()}"

def verify_password(password: str, encoded: str) -> bool:
    try:
        scheme, iterations, salt_hex, digest_hex = encoded.split("$")
        if scheme != "pbkdf2_sha256":
            return False
        actual = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), bytes.fromhex(salt_hex), int(iterations)).hex()
        return hmac.compare_digest(actual, digest_hex)
    except (ValueError, TypeError):
        return False

def register_user(full_name: str, email: str, password: str) -> tuple[bool, str, int | None]:
    full_name, email = full_name.strip(), email.strip().lower()
    if len(full_name) < 2:
        return False, "Enter your full name (at least 2 characters).", None
    if not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", email):
        return False, "Enter a valid email address.", None
    if len(password) < 8:
        return False, "Password must contain at least 8 characters.", None
    if database.get_user_by_email(email):
        return False, "An account with this email already exists.", None
    try:
        user_id = database.create_user(email, full_name, hash_password(password))
        return True, "Account created. You can now sign in.", user_id
    except Exception as exc:
        # Do not leak database internals to the UI.
        return False, "Could not create the account. Please try again.", None

def login_user(email: str, password: str) -> tuple[bool, str, dict | None]:
    user = database.get_user_by_email(email)
    if not user or not verify_password(password, user["password_hash"]):
        return False, "Email or password is incorrect.", None
    return True, "Signed in successfully.", {"id": user["id"], "email": user["email"], "full_name": user["full_name"]}
