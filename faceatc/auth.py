"""
Minimal admin authentication. Compares a SHA-256 hash instead of plaintext.
"""
import hashlib
from config import ADMIN_USERNAME, ADMIN_PASSWORD_HASH


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def verify_admin(username: str, password: str) -> bool:
    return username == ADMIN_USERNAME and hash_password(password) == ADMIN_PASSWORD_HASH
