import base64
import hashlib
import hmac
import json
from datetime import UTC, datetime, timedelta
from typing import Any

from app.core.config import get_settings

_TOKEN_ALGORITHM = "HS256"


def _base64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def _base64url_decode(data: str) -> bytes:
    padding = "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode(data + padding)


def _sign(signing_input: bytes, secret: str) -> bytes:
    return hmac.new(
        secret.encode("utf-8"),
        signing_input,
        hashlib.sha256,
    ).digest()


def create_access_token(
    subject: str,
    expires_delta: timedelta | None = None,
) -> str:
    settings = get_settings()
    if expires_delta is None:
        expires_delta = timedelta(minutes=settings.access_token_expire_minutes)
    expires_at = datetime.now(UTC) + expires_delta

    header = {"alg": _TOKEN_ALGORITHM, "typ": "JWT"}
    payload = {
        "sub": subject,
        "token_type": "access",
        "exp": int(expires_at.timestamp()),
    }

    encoded_header = _base64url_encode(
        json.dumps(header, separators=(",", ":")).encode("utf-8")
    )
    encoded_payload = _base64url_encode(
        json.dumps(payload, separators=(",", ":")).encode("utf-8")
    )
    signing_input = f"{encoded_header}.{encoded_payload}".encode("ascii")
    signature = _sign(signing_input, settings.token_secret)

    return f"{encoded_header}.{encoded_payload}.{_base64url_encode(signature)}"


def decode_access_token(token: str) -> dict[str, Any] | None:
    try:
        settings = get_settings()
        encoded_header, encoded_payload, encoded_signature = token.split(".", 2)
        signing_input = f"{encoded_header}.{encoded_payload}".encode("ascii")
        expected_signature = _sign(signing_input, settings.token_secret)
        actual_signature = _base64url_decode(encoded_signature)

        if not hmac.compare_digest(actual_signature, expected_signature):
            return None

        header = json.loads(_base64url_decode(encoded_header))
        if header != {"alg": _TOKEN_ALGORITHM, "typ": "JWT"}:
            return None

        payload = json.loads(_base64url_decode(encoded_payload))
        if payload.get("token_type") != "access":
            return None

        expires_at = payload.get("exp")
        if not isinstance(expires_at, int):
            return None
        if expires_at <= int(datetime.now(UTC).timestamp()):
            return None

        return payload
    except (ValueError, json.JSONDecodeError):
        return None
