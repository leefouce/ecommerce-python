from app.security.tokens import create_access_token, decode_access_token


def test_access_token_round_trip_includes_subject() -> None:
    token = create_access_token(subject="buyer@example.com")

    payload = decode_access_token(token)

    assert payload["sub"] == "buyer@example.com"
    assert payload["token_type"] == "access"


def test_decode_access_token_rejects_tampered_token() -> None:
    token = create_access_token(subject="buyer@example.com")
    tampered_token = token[:-1] + ("a" if token[-1] != "a" else "b")

    assert decode_access_token(tampered_token) is None
