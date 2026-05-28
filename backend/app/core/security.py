from datetime import datetime, timedelta, timezone
from hashlib import pbkdf2_hmac
from secrets import compare_digest, token_hex
from typing import Any

from jose import JWTError, jwt

from app.config import settings

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours
PBKDF2_ITERATIONS = 600_000
SALT_LENGTH = 32


def hash_password(password: str) -> str:
    salt = token_hex(SALT_LENGTH)
    dk = pbkdf2_hmac("sha256", password.encode(), salt.encode(), PBKDF2_ITERATIONS)
    return f"{salt}${dk.hex()}"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        salt, dk_hex = hashed_password.split("$")
        dk = pbkdf2_hmac("sha256", plain_password.encode(), salt.encode(), PBKDF2_ITERATIONS)
        return compare_digest(dk.hex(), dk_hex)
    except (ValueError, AttributeError):
        return False


def create_access_token(data: dict[str, Any], expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> dict[str, Any] | None:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None
