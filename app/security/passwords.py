import hashlib
import hmac
import os

_PBKDF2_ITERATIONS = 600_000
_SALT_BYTES = 16
_HASH_NAME = "sha256"


def hash_password(password: str) -> str:
    salt = os.urandom(_SALT_BYTES)
    password_hash = hashlib.pbkdf2_hmac(
        _HASH_NAME,
        password.encode("utf-8"),
        salt,
        _PBKDF2_ITERATIONS,
    )
    return f"pbkdf2_{_HASH_NAME}${_PBKDF2_ITERATIONS}${salt.hex()}${password_hash.hex()}"


def verify_password(password: str, password_hash: str) -> bool:
    try:
        algorithm, iterations_text, salt_hex, expected_hash_hex = password_hash.split("$", 3)
        if algorithm != f"pbkdf2_{_HASH_NAME}":
            return False

        iterations = int(iterations_text)
        if iterations <= 0:
            return False

        salt = bytes.fromhex(salt_hex)
        expected_hash = bytes.fromhex(expected_hash_hex)
        actual_hash = hashlib.pbkdf2_hmac(
            _HASH_NAME,
            password.encode("utf-8"),
            salt,
            iterations,
        )
    except (ValueError, TypeError):
        return False

    return hmac.compare_digest(actual_hash, expected_hash)
