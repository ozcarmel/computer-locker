import tempfile
import unittest
from pathlib import Path

from activity_reporter import (
    APP_SAMPLE_EVENT,
    read_jsonl,
    summarize_app_usage,
    write_jsonl,
)


class ActivityReporterTests(unittest.TestCase):
    def test_jsonl_helpers_round_trip_events(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "events.jsonl"
            write_jsonl(path, {"eventType": APP_SAMPLE_EVENT, "processName": "chrome.exe"})

            self.assertEqual(read_jsonl(path)[0]["processName"], "chrome.exe")

    def test_app_usage_summary_groups_by_process(self):
        events = [
            {
                "eventType": APP_SAMPLE_EVENT,
                "processName": "chrome.exe",
                "windowTitle": "Homework",
                "durationSeconds": 30,
            },
            {
                "eventType": APP_SAMPLE_EVENT,
                "processName": "chrome.exe",
                "windowTitle": "Homework",
                "durationSeconds": 30,
            },
            {
                "eventType": APP_SAMPLE_EVENT,
                "processName": "roblox.exe",
                "windowTitle": "Roblox",
                "durationSeconds": 30,
            },
        ]

        summary = summarize_app_usage(events)

        self.assertEqual(summary[0]["appName"], "chrome.exe")
        self.assertEqual(summary[0]["seconds"], 60)
        self.assertEqual(summary[0]["topWindowTitles"], ["Homework"])
        self.assertEqual(summary[1]["appName"], "roblox.exe")


if __name__ == "__main__":
    unittest.main()
