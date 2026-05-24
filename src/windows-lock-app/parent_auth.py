import hashlib
import os


def configured_parent_password():
    return os.environ.get("LOCK_APP_PARENT_PASSWORD", "")


def configured_parent_password_hash():
    return os.environ.get("LOCK_APP_PARENT_PASSWORD_HASH", "")


def hash_password(password):
    if password is None:
        return ""
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def verify_parent_password(candidate, expected_password=None):
    if expected_password is not None:
        return bool(expected_password) and candidate == expected_password

    expected_hash = configured_parent_password_hash()
    if expected_hash:
        return hash_password(candidate or "") == expected_hash

    expected = configured_parent_password()
    return bool(expected) and candidate == expected
