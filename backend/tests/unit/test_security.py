from datetime import timedelta

import pytest

from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_access_token,
    decode_refresh_token,
    hash_password,
    verify_password,
)


def test_hash_and_verify_correct_password():
    hashed = hash_password("mypassword")
    assert verify_password("mypassword", hashed) is True


def test_hash_and_verify_wrong_password():
    hashed = hash_password("mypassword")
    assert verify_password("wrongpassword", hashed) is False


def test_hash_and_verify_empty_password():
    hashed = hash_password("")
    assert verify_password("", hashed) is True
    assert verify_password("notempty", hashed) is False


def test_different_passwords_different_hashes():
    h1 = hash_password("password1")
    h2 = hash_password("password2")
    assert h1 != h2


def test_same_password_different_hashes():
    h1 = hash_password("samepass")
    h2 = hash_password("samepass")
    assert h1 != h2


def test_access_token_round_trip():
    data = {"sub": "user-123", "role": "student"}
    token = create_access_token(data)
    decoded = decode_access_token(token)
    assert decoded is not None
    assert decoded["sub"] == "user-123"
    assert decoded["role"] == "student"


def test_access_token_expired():
    data = {"sub": "user-123"}
    token = create_access_token(data, expires_delta=timedelta(seconds=-1))
    assert decode_access_token(token) is None


def test_access_token_tampered():
    token = create_access_token({"sub": "user-123"})
    tampered = token[:-5] + "XXXXX"
    assert decode_access_token(tampered) is None


def test_refresh_token_round_trip():
    data = {"sub": "user-456"}
    token = create_refresh_token(data)
    decoded = decode_refresh_token(token)
    assert decoded is not None
    assert decoded["sub"] == "user-456"
    assert decoded["type"] == "refresh"


def test_refresh_token_has_type_refresh():
    token = create_refresh_token({"sub": "abc"})
    decoded = decode_refresh_token(token)
    assert decoded is not None
    assert decoded["type"] == "refresh"


def test_refresh_token_rejects_access_token():
    access_token = create_access_token({"sub": "abc"})
    assert decode_refresh_token(access_token) is None


def test_refresh_token_expired():
    from unittest.mock import patch
    from datetime import datetime, timezone

    data = {"sub": "user-789"}
    with patch(
        "app.core.security.datetime",
        wraps=__import__("datetime").datetime,
    ) as mock_dt:
        past = datetime.now(timezone.utc) - timedelta(days=30)
        mock_dt.now.return_value = past
        token = create_refresh_token(data)

    assert decode_refresh_token(token) is None
