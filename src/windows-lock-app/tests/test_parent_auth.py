import unittest

from parent_auth import verify_parent_password


class ParentAuthTests(unittest.TestCase):
    def test_accepts_matching_password(self):
        self.assertTrue(verify_parent_password("secret", "secret"))

    def test_rejects_wrong_password(self):
        self.assertFalse(verify_parent_password("wrong", "secret"))

    def test_rejects_empty_expected_password(self):
        self.assertFalse(verify_parent_password("", ""))
        self.assertFalse(verify_parent_password("anything", ""))


if __name__ == "__main__":
    unittest.main()
