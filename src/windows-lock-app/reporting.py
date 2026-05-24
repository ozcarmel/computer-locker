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

EVENT_LABELS = {
    APP_STARTED_EVENT: "App started",
    USAGE_EVENT: "Usage interval completed",
    REGULAR_LOCK_STARTED_EVENT: "Break lock started",
    REGULAR_LOCK_RELEASED_EVENT: "Break lock released",
    DAILY_LIMIT_STARTED_EVENT: "Daily limit lock started",
    PARENT_EXTRA_GRANTED_EVENT: "Parent extra time granted",
    TEST_LOCK_STARTED_EVENT: "Test lock started",
    PARENT_ACTION_DENIED_EVENT: "Parent password denied",
    PARENT_EXIT_ALLOWED_EVENT: "Parent exit allowed",
}


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


def format_duration(seconds):
    seconds = max(0, int(seconds))
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    if hours:
        return f"{hours}h {minutes:02d}m"
    if minutes:
        return f"{minutes}m {seconds:02d}s"
    return f"{seconds}s"


def event_display_name(event_type):
    return EVENT_LABELS.get(event_type, event_type.replace("_", " ").title())


def event_detail_text(event):
    details = event.get("details", {})
    event_type = event.get("eventType", "")

    if event_type == APP_STARTED_EVENT:
        return (
            "work "
            f"{format_duration(details.get('workSeconds', 0))}, "
            "break "
            f"{format_duration(details.get('breakSeconds', 0))}, "
            "daily limit "
            f"{format_duration(details.get('dailyLimitSeconds', 0))}"
        )
    if event_type == USAGE_EVENT:
        return (
            f"used {format_duration(details.get('durationSeconds', 0))}; "
            f"total today {format_duration(details.get('unlockedSecondsToday', 0))}; "
            f"cycles {details.get('completedCycles', 0)}"
        )
    if event_type == REGULAR_LOCK_STARTED_EVENT:
        return (
            f"break length {format_duration(details.get('breakSeconds', 0))}; "
            f"cycles {details.get('completedCycles', 0)}"
        )
    if event_type == DAILY_LIMIT_STARTED_EVENT:
        return (
            f"used today {format_duration(details.get('unlockedSecondsToday', 0))}; "
            f"limit {format_duration(details.get('effectiveDailyLimitSeconds', 0))}"
        )
    if event_type == PARENT_EXTRA_GRANTED_EVENT:
        return (
            f"granted {format_duration(details.get('grantedSeconds', 0))}; "
            f"extra today {format_duration(details.get('parentExtraSecondsToday', 0))}"
        )
    if event_type == PARENT_ACTION_DENIED_EVENT:
        return f"action: {details.get('action', 'parent action')}"

    return ""


def build_event_report(events):
    events_by_date = defaultdict(list)
    for event in sorted(events, key=lambda item: item.get("timestamp", "")):
        events_by_date[event.get("date", "Unknown date")].append(event)

    daily_report = build_daily_report(events)
    lines = [
        "Computer Locker Event Report",
        "=" * 28,
        "",
    ]

    if not events:
        lines.append("No events were recorded.")
        return "\n".join(lines) + "\n"

    for day in sorted(events_by_date):
        summary = daily_report.get(day, {})
        day_events = events_by_date[day]

        lines.extend(
            [
                day,
                "-" * len(day),
                f"Total unlocked usage: {format_duration(summary.get('unlockedUsageSeconds', 0))}",
                f"Regular break locks: {summary.get('regularLockAppearances', 0)}",
                f"Daily limit locks: {summary.get('dailyLimitLockAppearances', 0)}",
                f"Parent extra time granted: {format_duration(summary.get('parentExtraSecondsGranted', 0))}",
                f"Test locks: {summary.get('testLockAppearances', 0)}",
                f"Denied parent actions: {summary.get('parentActionDeniedCount', 0)}",
                f"Parent exits: {summary.get('parentExitAllowedCount', 0)}",
                "",
                "Timeline",
                "--------",
            ]
        )

        for event in day_events:
            timestamp = event.get("timestamp", "")
            time = timestamp[11:19] if len(timestamp) >= 19 else "--:--:--"
            username = event.get("windowsUsername") or "unknown user"
            label = event_display_name(event.get("eventType", "unknown"))
            detail = event_detail_text(event)
            suffix = f" - {detail}" if detail else ""
            lines.append(f"{time} | {label} | {username}{suffix}")

        lines.append("")

    return "\n".join(lines)
