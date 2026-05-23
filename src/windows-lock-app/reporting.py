import json
import os
from collections import defaultdict
from datetime import datetime
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_EVENTS_DIR = PROJECT_ROOT / "data" / "events"

USAGE_EVENT = "usage_interval_completed"
REGULAR_LOCK_STARTED_EVENT = "regular_lock_started"
REGULAR_LOCK_RELEASED_EVENT = "regular_lock_released"
DAILY_LIMIT_STARTED_EVENT = "daily_limit_lock_started"
PARENT_EXTRA_GRANTED_EVENT = "parent_extra_time_granted"
TEST_LOCK_STARTED_EVENT = "test_lock_started"
APP_STARTED_EVENT = "app_started"
PARENT_ACTION_DENIED_EVENT = "parent_action_denied"
PARENT_EXIT_ALLOWED_EVENT = "parent_exit_allowed"


class EventLogger:
    def __init__(self, events_dir=None, clock=None, username=None):
        self.events_dir = Path(events_dir or os.environ.get("LOCK_APP_EVENTS_DIR", DEFAULT_EVENTS_DIR))
        self.clock = clock or datetime.now
        self.username = username or os.environ.get("USERNAME", "")

    def log(self, event_type, **details):
        now = self.clock()
        event = {
            "eventType": event_type,
            "timestamp": now.isoformat(timespec="seconds"),
            "date": now.date().isoformat(),
            "windowsUsername": self.username,
            "details": details,
        }

        self.events_dir.mkdir(parents=True, exist_ok=True)
        with self._events_file(now).open("a", encoding="utf-8") as file:
            file.write(json.dumps(event, sort_keys=True) + "\n")
        return event

    def _events_file(self, now):
        return self.events_dir / f"{now.date().isoformat()}.jsonl"


def load_events(events_dir=None):
    directory = Path(events_dir or os.environ.get("LOCK_APP_EVENTS_DIR", DEFAULT_EVENTS_DIR))
    if not directory.exists():
        return []

    events = []
    for path in sorted(directory.glob("*.jsonl")):
        with path.open("r", encoding="utf-8") as file:
            for line in file:
                line = line.strip()
                if line:
                    events.append(json.loads(line))
    return events


def build_daily_report(events):
    report = defaultdict(
        lambda: {
            "unlockedUsageSeconds": 0,
            "regularLockAppearances": 0,
            "dailyLimitLockAppearances": 0,
            "parentExtraSecondsGranted": 0,
            "testLockAppearances": 0,
            "parentActionDeniedCount": 0,
            "parentExitAllowedCount": 0,
        }
    )

    for event in events:
        day = event["date"]
        details = event.get("details", {})

        if event["eventType"] == USAGE_EVENT:
            report[day]["unlockedUsageSeconds"] += int(details.get("durationSeconds", 0))
        elif event["eventType"] == REGULAR_LOCK_STARTED_EVENT:
            report[day]["regularLockAppearances"] += 1
        elif event["eventType"] == DAILY_LIMIT_STARTED_EVENT:
            report[day]["dailyLimitLockAppearances"] += 1
        elif event["eventType"] == PARENT_EXTRA_GRANTED_EVENT:
            report[day]["parentExtraSecondsGranted"] += int(details.get("grantedSeconds", 0))
        elif event["eventType"] == TEST_LOCK_STARTED_EVENT:
            report[day]["testLockAppearances"] += 1
        elif event["eventType"] == PARENT_ACTION_DENIED_EVENT:
            report[day]["parentActionDeniedCount"] += 1
        elif event["eventType"] == PARENT_EXIT_ALLOWED_EVENT:
            report[day]["parentExitAllowedCount"] += 1

    return dict(sorted(report.items()))
