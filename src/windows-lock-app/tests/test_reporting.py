import json
import tempfile
import unittest
from datetime import datetime
from pathlib import Path

from reporting import (
    DAILY_LIMIT_STARTED_EVENT,
    EventLogger,
    PARENT_EXTRA_GRANTED_EVENT,
    PARENT_ACTION_DENIED_EVENT,
    PARENT_EXIT_ALLOWED_EVENT,
    REGULAR_LOCK_STARTED_EVENT,
    TEST_LOCK_STARTED_EVENT,
    USAGE_EVENT,
    build_daily_report,
    build_event_report,
    load_events,
)


class ReportingTests(unittest.TestCase):
    def test_event_logger_writes_jsonl_events(self):
        with tempfile.TemporaryDirectory() as directory:
            logger = EventLogger(
                events_dir=directory,
                clock=lambda: datetime(2026, 5, 23, 9, 0, 0),
                username="child",
            )

            event = logger.log(USAGE_EVENT, durationSeconds=1200)
            path = Path(directory) / "2026-05-23.jsonl"

            self.assertTrue(path.exists())
            stored = json.loads(path.read_text(encoding="utf-8").strip())
            self.assertEqual(stored, event)
            self.assertEqual(stored["windowsUsername"], "child")

    def test_load_events_reads_all_event_files(self):
        with tempfile.TemporaryDirectory() as directory:
            first = EventLogger(
                events_dir=directory,
                clock=lambda: datetime(2026, 5, 23, 9, 0, 0),
            )
            second = EventLogger(
                events_dir=directory,
                clock=lambda: datetime(2026, 5, 24, 9, 0, 0),
            )

            first.log(USAGE_EVENT, durationSeconds=60)
            second.log(REGULAR_LOCK_STARTED_EVENT)

            events = load_events(directory)
            self.assertEqual([event["date"] for event in events], ["2026-05-23", "2026-05-24"])

    def test_daily_report_summarizes_usage_and_locks(self):
        events = [
            {
                "date": "2026-05-23",
                "eventType": USAGE_EVENT,
                "details": {"durationSeconds": 1200},
            },
            {
                "date": "2026-05-23",
                "eventType": USAGE_EVENT,
                "details": {"durationSeconds": 600},
            },
            {
                "date": "2026-05-23",
                "eventType": REGULAR_LOCK_STARTED_EVENT,
                "details": {},
            },
            {
                "date": "2026-05-23",
                "eventType": DAILY_LIMIT_STARTED_EVENT,
                "details": {},
            },
            {
                "date": "2026-05-23",
                "eventType": PARENT_EXTRA_GRANTED_EVENT,
                "details": {"grantedSeconds": 1200},
            },
            {
                "date": "2026-05-23",
                "eventType": TEST_LOCK_STARTED_EVENT,
                "details": {},
            },
            {
                "date": "2026-05-23",
                "eventType": PARENT_ACTION_DENIED_EVENT,
                "details": {},
            },
            {
                "date": "2026-05-23",
                "eventType": PARENT_EXIT_ALLOWED_EVENT,
                "details": {},
            },
        ]

        report = build_daily_report(events)

        self.assertEqual(report["2026-05-23"]["unlockedUsageSeconds"], 1800)
        self.assertEqual(report["2026-05-23"]["regularLockAppearances"], 1)
        self.assertEqual(report["2026-05-23"]["dailyLimitLockAppearances"], 1)
        self.assertEqual(report["2026-05-23"]["parentExtraSecondsGranted"], 1200)
        self.assertEqual(report["2026-05-23"]["testLockAppearances"], 1)
        self.assertEqual(report["2026-05-23"]["parentActionDeniedCount"], 1)
        self.assertEqual(report["2026-05-23"]["parentExitAllowedCount"], 1)

    def test_event_report_formats_parent_friendly_timeline(self):
        events = [
            {
                "date": "2026-05-24",
                "timestamp": "2026-05-24T10:25:01",
                "windowsUsername": "gilic",
                "eventType": TEST_LOCK_STARTED_EVENT,
                "details": {},
            },
            {
                "date": "2026-05-24",
                "timestamp": "2026-05-24T10:25:08",
                "windowsUsername": "gilic",
                "eventType": REGULAR_LOCK_STARTED_EVENT,
                "details": {"breakSeconds": 1200, "completedCycles": 1},
            },
        ]

        report = build_event_report(events)

        self.assertIn("Computer Locker Event Report", report)
        self.assertIn("2026-05-24", report)
        self.assertIn("Timeline", report)
        self.assertIn("10:25:01 | Test lock started | gilic", report)
        self.assertIn("10:25:08 | Break lock started | gilic - break length 20m 00s; cycles 1", report)


if __name__ == "__main__":
    unittest.main()
