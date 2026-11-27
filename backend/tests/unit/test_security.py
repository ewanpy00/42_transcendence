from datetime import UTC, datetime, timedelta

import jwt
import pytest

from app.core.config import get_settings
from app.core.security import (
    InvalidTokenError,
    create_token,
    decode_token,
    hash_password,
    verify_password,
)


def test_password_is_hashed_and_salted():
    first = hash_password("correct horse")
    second = hash_password("correct horse")

    assert first != "correct horse"
    assert first.startswith("$argon2id$")
    assert first != second
    assert verify_password("correct horse", first)
    assert not verify_password("wrong horse", first)


def test_verify_without_hash_is_false():
    assert not verify_password("anything", None)


def test_token_roundtrip():
    token, issued = create_token("42", "access")
    payload = decode_token(token, "access")

    assert payload.sub == "42"
    assert payload.jti == issued.jti


def test_token_type_is_checked():
    token, _ = create_token("42", "refresh")
    with pytest.raises(InvalidTokenError):
        decode_token(token, "access")


def test_expired_token_is_rejected():
    settings = get_settings()
    token = jwt.encode(
        {"sub": "42", "type": "access", "jti": "x", "exp": datetime.now(UTC) - timedelta(seconds=1)},
        settings.secret_key,
        algorithm=settings.jwt_algorithm,
    )
    with pytest.raises(InvalidTokenError):
        decode_token(token, "access")


def test_token_signed_with_other_key_is_rejected():
    token = jwt.encode(
        {"sub": "42", "type": "access", "jti": "x", "exp": datetime.now(UTC) + timedelta(minutes=5)},
        "another-secret-key-that-is-long-enough-0123456789",
        algorithm="HS256",
    )
    with pytest.raises(InvalidTokenError):
        decode_token(token, "access")


def test_short_secret_key_is_refused(monkeypatch):
    monkeypatch.setattr(get_settings(), "secret_key", "short")
    with pytest.raises(RuntimeError):
        create_token("42", "access")
