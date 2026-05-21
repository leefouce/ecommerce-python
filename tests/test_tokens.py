from datetime import timedelta

from app.core.config import get_settings
from app.security.tokens import create_access_token, decode_access_token


def test_access_token_round_trip_includes_subject() -> None:
    token = create_access_token(subject="buyer@example.com")

    payload = decode_access_token(token)

    assert payload is not None
    assert payload["sub"] == "buyer@example.com"
    assert payload["token_type"] == "access"


def test_access_token_payload_includes_expiration() -> None:
    token = create_access_token(subject="buyer@example.com")

    payload = decode_access_token(token)

    assert payload is not None
    assert isinstance(payload["exp"], int)


def test_decode_access_token_rejects_expired_token() -> None:
    token = create_access_token(
        subject="buyer@example.com",
        expires_delta=timedelta(seconds=-1),
    )

    assert decode_access_token(token) is None


def test_access_token_secret_comes_from_environment(monkeypatch) -> None:
    monkeypatch.setenv("APP_TOKEN_SECRET", "test-secret-one")
    assert get_settings().token_secret == "test-secret-one"
    token = create_access_token(subject="buyer@example.com")

    monkeypatch.setenv("APP_TOKEN_SECRET", "test-secret-two")

    assert decode_access_token(token) is None


def test_decode_access_token_rejects_tampered_token() -> None:
    token = create_access_token(subject="buyer@example.com")
    encoded_header, encoded_payload, encoded_signature = token.split(".")
    replacement = "A" if encoded_payload[0] != "A" else "B"
    tampered_payload = replacement + encoded_payload[1:]
    tampered_token = f"{encoded_header}.{tampered_payload}.{encoded_signature}"

    assert decode_access_token(tampered_token) is None
