import unittest
from unittest.mock import patch

from parent_auth import configured_parent_password, hash_password, verify_parent_password


class ParentAuthTests(unittest.TestCase):
    def test_no_default_parent_password(self):
        with patch.dict("os.environ", {}, clear=True):
            self.assertEqual(configured_parent_password(), "")

    def test_reads_password_from_environment(self):
        with patch.dict("os.environ", {"LOCK_APP_PARENT_PASSWORD": "secret"}, clear=True):
            self.assertEqual(configured_parent_password(), "secret")

    def test_accepts_matching_password_hash_from_environment(self):
        with patch.dict("os.environ", {"LOCK_APP_PARENT_PASSWORD_HASH": hash_password("secret")}, clear=True):
            self.assertTrue(verify_parent_password("secret"))
            self.assertFalse(verify_parent_password("wrong"))

    def test_accepts_matching_password(self):
        self.assertTrue(verify_parent_password("secret", "secret"))

    def test_rejects_wrong_password(self):
        self.assertFalse(verify_parent_password("wrong", "secret"))

    def test_rejects_empty_expected_password(self):
        self.assertFalse(verify_parent_password("", ""))
        self.assertFalse(verify_parent_password("anything", ""))

    def test_rejects_none_candidate(self):
        self.assertFalse(verify_parent_password(None, "secret"))


if __name__ == "__main__":
    unittest.main()
