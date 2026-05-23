import unittest

from countdown import format_seconds, next_remaining_seconds


class CountdownTests(unittest.TestCase):
    def test_format_seconds_uses_minutes_and_seconds(self):
        self.assertEqual(format_seconds(20 * 60), "20:00")
        self.assertEqual(format_seconds(61), "01:01")
        self.assertEqual(format_seconds(0), "00:00")

    def test_format_seconds_never_goes_negative(self):
        self.assertEqual(format_seconds(-10), "00:00")

    def test_next_remaining_seconds_counts_down_to_zero(self):
        self.assertEqual(next_remaining_seconds(100, 1200, 100), 1200)
        self.assertEqual(next_remaining_seconds(100, 1200, 160), 1140)
        self.assertEqual(next_remaining_seconds(100, 1200, 1400), 0)


if __name__ == "__main__":
    unittest.main()
