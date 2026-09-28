from datetime import UTC, datetime, timedelta

import bcrypt
import jwt

from app.core.config import get_settings

# bcrypt silently truncates anything longer than 72 bytes.
MAX_PASSWORD_BYTES = 72


def hash_password(plain_password: str) -> str:
    return bcrypt.hashpw(
        plain_password.encode("utf-8")[:MAX_PASSWORD_BYTES],
        bcrypt.gensalt()
    ).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return bcrypt.checkpw(
            plain_password.encode("utf-8")[:MAX_PASSWORD_BYTES],
            hashed_password.encode("utf-8")
        )
    except ValueError:
        return False


def create_access_token(
        subject: str,
        role: str,
        expires_delta: timedelta | None = None
) -> str:

    settings = get_settings()

    expire_minutes = settings.jwt_access_token_expire_minutes
    expires_at = datetime.now(UTC) + (
        expires_delta or timedelta(minutes=expire_minutes)
    )

    payload = {
        "sub": subject,
        "role": role,
        "iat": int(datetime.now(UTC).timestamp()),
        "exp": int(expires_at.timestamp())
    }

    return jwt.encode(
        payload,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm
    )


def decode_access_token(token: str) -> dict | None:
    settings = get_settings()

    try:
        return jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm]
        )
    except jwt.PyJWTError:
        return None
