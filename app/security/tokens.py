import base64
import hashlib
import hmac
import json
from typing import Any

_TOKEN_SECRET = "development-secret-change-me"
_TOKEN_ALGORITHM = "HS256"


def _base64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def _base64url_decode(data: str) -> bytes:
    padding = "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode(data + padding)


def create_access_token(subject: str) -> str:
    header = {"alg": _TOKEN_ALGORITHM, "typ": "JWT"}
    payload = {"sub": subject, "token_type": "access"}

    encoded_header = _base64url_encode(
        json.dumps(header, separators=(",", ":")).encode("utf-8")
    )
    encoded_payload = _base64url_encode(
        json.dumps(payload, separators=(",", ":")).encode("utf-8")
    )
    signing_input = f"{encoded_header}.{encoded_payload}".encode("ascii")
    signature = hmac.new(
        _TOKEN_SECRET.encode("utf-8"),
        signing_input,
        hashlib.sha256,
    ).digest()

    return f"{encoded_header}.{encoded_payload}.{_base64url_encode(signature)}"


def decode_access_token(token: str) -> dict[str, Any] | None:
    try:
        encoded_header, encoded_payload, encoded_signature = token.split(".", 2)
        signing_input = f"{encoded_header}.{encoded_payload}".encode("ascii")
        expected_signature = hmac.new(
            _TOKEN_SECRET.encode("utf-8"),
            signing_input,
            hashlib.sha256,
        ).digest()
        actual_signature = _base64url_decode(encoded_signature)

        if not hmac.compare_digest(actual_signature, expected_signature):
            return None

        header = json.loads(_base64url_decode(encoded_header))
        if header != {"alg": _TOKEN_ALGORITHM, "typ": "JWT"}:
            return None

        payload = json.loads(_base64url_decode(encoded_payload))
        if payload.get("token_type") != "access":
            return None
        return payload
    except (ValueError, json.JSONDecodeError):
        return None
