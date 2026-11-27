"""Password hashing and JWT helpers."""

import uuid
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Literal

import jwt
from pwdlib import PasswordHash

from app.core.config import get_settings

TokenType = Literal["access", "refresh"]

# Argon2id with the library's recommended parameters.
_password_hash = PasswordHash.recommended()

# Verified against when the user does not exist, so a failed login takes
# the same time whether or not the email is registered.
_DUMMY_HASH = _password_hash.hash("not-a-real-password")


class InvalidTokenError(Exception):
    """The token is malformed, expired, signed with another key or of the wrong type."""


@dataclass(frozen=True)
class TokenPayload:
    sub: str
    type: TokenType
    jti: str
    exp: datetime


def hash_password(password: str) -> str:
    return _password_hash.hash(password)


def verify_password(password: str, hashed: str | None) -> bool:
    if hashed is None:
        _password_hash.verify(password, _DUMMY_HASH)
        return False
    return _password_hash.verify(password, hashed)


def _secret_key() -> str:
    key = get_settings().secret_key
    if len(key) < 32:
        raise RuntimeError("SECRET_KEY must be set and at least 32 characters long")
    return key


def create_token(subject: str, token_type: TokenType) -> tuple[str, TokenPayload]:
    settings = get_settings()
    lifetime = (
        timedelta(minutes=settings.access_token_expire_minutes)
        if token_type == "access"
        else timedelta(days=settings.refresh_token_expire_days)
    )
    now = datetime.now(UTC)
    payload = TokenPayload(
        sub=subject,
        type=token_type,
        jti=uuid.uuid4().hex,
        exp=now + lifetime,
    )
    token = jwt.encode(
        {
            "sub": payload.sub,
            "type": payload.type,
            "jti": payload.jti,
            "iat": now,
            "exp": payload.exp,
        },
        _secret_key(),
        algorithm=settings.jwt_algorithm,
    )
    return token, payload


def decode_token(token: str, expected_type: TokenType) -> TokenPayload:
    settings = get_settings()
    try:
        claims = jwt.decode(
            token,
            _secret_key(),
            algorithms=[settings.jwt_algorithm],
            options={"require": ["sub", "type", "jti", "exp"]},
        )
    except jwt.PyJWTError as exc:
        raise InvalidTokenError(str(exc)) from exc

    if claims["type"] != expected_type:
        raise InvalidTokenError(f"expected a {expected_type} token")

    return TokenPayload(
        sub=claims["sub"],
        type=claims["type"],
        jti=claims["jti"],
        exp=datetime.fromtimestamp(claims["exp"], UTC),
    )
