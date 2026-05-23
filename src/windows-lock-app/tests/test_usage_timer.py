import unittest
from datetime import datetime, time, timedelta

from usage_timer import UsageTimer, UsageTimerSettings


class UsageTimerTests(unittest.TestCase):
    def test_work_interval_triggers_break(self):
        settings = UsageTimerSettings(work_seconds=5, break_seconds=5, daily_limit_seconds=30)
        started = datetime(2026, 5, 23, 9, 0, 0)
        timer = UsageTimer(settings, now=started)

        timer.start_unlocked_interval(started)

        self.assertFalse(timer.should_start_break(started + timedelta(seconds=4)))
        self.assertTrue(timer.should_start_break(started + timedelta(seconds=5)))

    def test_begin_break_counts_usage_and_cycles(self):
        settings = UsageTimerSettings(work_seconds=5, break_seconds=5, daily_limit_seconds=30)
        started = datetime(2026, 5, 23, 9, 0, 0)
        timer = UsageTimer(settings, now=started)

        timer.start_unlocked_interval(started)
        lock_kind, elapsed_seconds = timer.begin_break(started + timedelta(seconds=5))
        status = timer.status(started + timedelta(seconds=5))

        self.assertEqual(lock_kind, "break")
        self.assertEqual(elapsed_seconds, 5)
        self.assertEqual(status["unlocked_seconds_today"], 5)
        self.assertEqual(status["completed_cycles"], 1)

    def test_daily_limit_detected_after_max_cycles(self):
        settings = UsageTimerSettings(work_seconds=5, break_seconds=5, daily_limit_seconds=10)
        started = datetime(2026, 5, 23, 9, 0, 0)
        timer = UsageTimer(settings, now=started)

        timer.start_unlocked_interval(started)
        self.assertEqual(timer.begin_break(started + timedelta(seconds=5))[0], "break")
        timer.finish_break(started + timedelta(seconds=10))
        self.assertEqual(timer.begin_break(started + timedelta(seconds=15))[0], "daily_limit")

        self.assertTrue(timer.status(started + timedelta(seconds=15))["daily_limit_reached"])

    def test_parent_extra_time_is_limited_and_reopens_usage(self):
        settings = UsageTimerSettings(
            work_seconds=5,
            break_seconds=5,
            daily_limit_seconds=10,
            parent_extra_seconds_limit=20,
        )
        started = datetime(2026, 5, 23, 9, 0, 0)
        timer = UsageTimer(settings, now=started)

        timer.start_unlocked_interval(started)
        timer.begin_break(started + timedelta(seconds=10))

        self.assertTrue(timer.status(started + timedelta(seconds=10))["daily_limit_reached"])

        granted = timer.grant_parent_extra_time(30, started + timedelta(seconds=11))
        status = timer.status(started + timedelta(seconds=11))

        self.assertEqual(granted, 20)
        self.assertFalse(status["daily_limit_reached"])
        self.assertEqual(status["parent_extra_seconds_today"], 20)
        self.assertEqual(status["parent_extra_seconds_remaining"], 0)
        self.assertTrue(timer.active_interval_started_at is not None)

    def test_parent_extra_time_resets_at_configured_reset_time(self):
        settings = UsageTimerSettings(
            work_seconds=5,
            break_seconds=5,
            daily_limit_seconds=10,
            parent_extra_seconds_limit=20,
            daily_reset_time=time(hour=8, minute=0),
        )
        started = datetime(2026, 5, 23, 9, 0, 0)
        timer = UsageTimer(settings, now=started)

        timer.grant_parent_extra_time(20, started)
        self.assertEqual(timer.status(started)["parent_extra_seconds_today"], 20)

        next_day = datetime(2026, 5, 24, 8, 0, 0)
        self.assertEqual(timer.status(next_day)["parent_extra_seconds_today"], 0)

    def test_daily_usage_resets_at_configured_reset_time(self):
        settings = UsageTimerSettings(
            work_seconds=5,
            break_seconds=5,
            daily_limit_seconds=10,
            daily_reset_time=time(hour=8, minute=0),
        )
        started = datetime(2026, 5, 23, 7, 59, 0)
        timer = UsageTimer(settings, now=started)

        timer.start_unlocked_interval(started)
        timer.begin_break(started + timedelta(seconds=5))
        self.assertEqual(timer.status(started + timedelta(seconds=5))["unlocked_seconds_today"], 5)

        status = timer.status(datetime(2026, 5, 23, 8, 0, 0))
        self.assertEqual(status["unlocked_seconds_today"], 0)
        self.assertEqual(status["completed_cycles"], 0)


if __name__ == "__main__":
    unittest.main()
