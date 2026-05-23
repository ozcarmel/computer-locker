import os


def configured_parent_password():
    return os.environ.get("LOCK_APP_PARENT_PASSWORD", "parent")


def verify_parent_password(candidate, expected_password=None):
    expected = configured_parent_password() if expected_password is None else expected_password
    return bool(expected) and candidate == expected
