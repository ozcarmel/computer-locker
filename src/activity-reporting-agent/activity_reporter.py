import argparse
import ctypes
import json
import os
import shutil
import sqlite3
import time
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from pathlib import Path


DEFAULT_RUNTIME_DIR = Path(os.environ.get("PROGRAMDATA", r"C:\ProgramData")) / "Cultural Aspects"
DEFAULT_ACTIVITY_DIR = DEFAULT_RUNTIME_DIR / "activity"
DEFAULT_OUTPUT_PATH = DEFAULT_RUNTIME_DIR / "activity-report.json"
DEFAULT_LOCK_EVENTS_DIR = DEFAULT_RUNTIME_DIR / "data" / "events"

APP_SAMPLE_EVENT = "active_app_sample"


def now_local():
    return datetime.now()


def date_key(moment):
    return moment.date().isoformat()


def app_usage_path(activity_dir, moment):
    return Path(activity_dir) / "app-usage" / f"{date_key(moment)}.jsonl"


def write_jsonl(path, payload):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as file:
        file.write(json.dumps(payload, sort_keys=True) + "\n")


def read_jsonl(path):
    path = Path(path)
    if not path.exists():
        return []

    items = []
    with path.open("r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()
            if line:
                items.append(json.loads(line))
    return items


def load_jsonl_dir(directory):
    directory = Path(directory)
    if not directory.exists():
        return []

    items = []
    for path in sorted(directory.glob("*.jsonl")):
        items.extend(read_jsonl(path))
    return items


def process_name_from_path(path):
    if not path:
        return "Unknown app"
    return Path(path).name


def active_window_info():
    user32 = ctypes.windll.user32
    kernel32 = ctypes.windll.kernel32

    hwnd = user32.GetForegroundWindow()
    if not hwnd:
        return {"processName": "No active window", "windowTitle": "", "processPath": ""}

    title_length = user32.GetWindowTextLengthW(hwnd)
    title_buffer = ctypes.create_unicode_buffer(title_length + 1)
    user32.GetWindowTextW(hwnd, title_buffer, title_length + 1)

    process_id = ctypes.c_ulong()
    user32.GetWindowThreadProcessId(hwnd, ctypes.byref(process_id))

    process_path = ""
    PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
    handle = kernel32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, process_id.value)
    if handle:
        try:
            path_buffer = ctypes.create_unicode_buffer(32768)
            size = ctypes.c_ulong(len(path_buffer))
            if kernel32.QueryFullProcessImageNameW(handle, 0, path_buffer, ctypes.byref(size)):
                process_path = path_buffer.value
        finally:
            kernel32.CloseHandle(handle)

    return {
        "processName": process_name_from_path(process_path),
        "windowTitle": title_buffer.value,
        "processPath": process_path,
    }


def monitor(activity_dir=DEFAULT_ACTIVITY_DIR, interval_seconds=30):
    interval_seconds = max(5, int(interval_seconds))
    while True:
        moment = now_local()
        info = active_window_info()
        write_jsonl(
            app_usage_path(activity_dir, moment),
            {
                "eventType": APP_SAMPLE_EVENT,
                "timestamp": moment.isoformat(timespec="seconds"),
                "date": date_key(moment),
                "durationSeconds": interval_seconds,
                **info,
            },
        )
        time.sleep(interval_seconds)


def summarize_app_usage(events):
    usage = defaultdict(int)
    titles = defaultdict(Counter)

    for event in events:
        if event.get("eventType") != APP_SAMPLE_EVENT:
            continue

        app = event.get("processName") or "Unknown app"
        usage[app] += int(event.get("durationSeconds", 0))
        title = (event.get("windowTitle") or "").strip()
        if title:
            titles[app][title] += 1

    rows = []
    for app, seconds in usage.items():
        common_titles = [title for title, _count in titles[app].most_common(3)]
        rows.append(
            {
                "appName": app,
                "seconds": seconds,
                "topWindowTitles": common_titles,
            }
        )

    return sorted(rows, key=lambda row: (-row["seconds"], row["appName"].lower()))


def browser_history_locations(home_dir=None):
    home = Path(home_dir or Path.home())
    local_app_data = Path(os.environ.get("LOCALAPPDATA", home / "AppData" / "Local"))
    roaming_app_data = Path(os.environ.get("APPDATA", home / "AppData" / "Roaming"))

    return [
        ("Chrome", local_app_data / "Google" / "Chrome" / "User Data" / "Default" / "History"),
        ("Edge", local_app_data / "Microsoft" / "Edge" / "User Data" / "Default" / "History"),
        ("Firefox", roaming_app_data / "Mozilla" / "Firefox" / "Profiles"),
    ]


def chrome_time_to_datetime(value):
    try:
        timestamp = int(value)
    except (TypeError, ValueError):
        return None

    if timestamp <= 0:
        return None

    return datetime(1601, 1, 1) + timedelta(microseconds=timestamp)


def unix_time_to_datetime(value):
    try:
        timestamp = int(value)
    except (TypeError, ValueError):
        return None

    if timestamp <= 0:
        return None

    return datetime.fromtimestamp(timestamp / 1_000_000)


def copy_database(source, temp_dir, label):
    source = Path(source)
    try:
        if not source.exists() or source.is_dir():
            return None
    except OSError:
        return None

    target = Path(temp_dir) / f"{label}-{int(time.time() * 1000)}.sqlite"
    try:
        shutil.copy2(source, target)
        return target
    except OSError:
        return None


def read_chromium_history(browser_name, history_path, start_time, temp_dir, limit=200):
    copy_path = copy_database(history_path, temp_dir, browser_name)
    if not copy_path:
        return []

    entries = []
    try:
        with sqlite3.connect(copy_path) as connection:
            for url, title, last_visit_time in connection.execute(
                "select url, title, last_visit_time from urls order by last_visit_time desc limit ?",
                (limit,),
            ):
                visited_at = chrome_time_to_datetime(last_visit_time)
                if visited_at and visited_at >= start_time:
                    entries.append(
                        {
                            "browser": browser_name,
                            "visitedAt": visited_at.isoformat(timespec="seconds"),
                            "title": title or "",
                            "url": url,
                        }
                    )
    except sqlite3.Error:
        return []
    finally:
        try:
            copy_path.unlink()
        except OSError:
            pass

    return entries


def read_firefox_history(profile_root, start_time, temp_dir, limit=200):
    profile_root = Path(profile_root)
    if not profile_root.exists():
        return []

    entries = []
    for places_path in profile_root.glob("*/places.sqlite"):
        copy_path = copy_database(places_path, temp_dir, "Firefox")
        if not copy_path:
            continue

        try:
            with sqlite3.connect(copy_path) as connection:
                rows = connection.execute(
                    """
                    select p.url, p.title, v.visit_date
                    from moz_places p
                    join moz_historyvisits v on p.id = v.place_id
                    order by v.visit_date desc
                    limit ?
                    """,
                    (limit,),
                )
                for url, title, visit_date in rows:
                    visited_at = unix_time_to_datetime(visit_date)
                    if visited_at and visited_at >= start_time:
                        entries.append(
                            {
                                "browser": "Firefox",
                                "visitedAt": visited_at.isoformat(timespec="seconds"),
                                "title": title or "",
                                "url": url,
                            }
                        )
        except sqlite3.Error:
            pass
        finally:
            try:
                copy_path.unlink()
            except OSError:
                pass

    return entries


def read_browser_history(start_time, temp_dir, home_dir=None):
    entries = []
    for browser_name, path in browser_history_locations(home_dir):
        if browser_name in ("Chrome", "Edge"):
            entries.extend(read_chromium_history(browser_name, path, start_time, temp_dir))
        elif browser_name == "Firefox":
            entries.extend(read_firefox_history(path, start_time, temp_dir))

    return sorted(entries, key=lambda item: item["visitedAt"], reverse=True)


def load_lock_events(lock_events_dir, start_time):
    events = []
    for event in load_jsonl_dir(lock_events_dir):
        timestamp = event.get("timestamp")
        if not timestamp:
            continue

        try:
            event_time = datetime.fromisoformat(timestamp)
        except ValueError:
            continue

        if event_time >= start_time:
            events.append(
                {
                    "time": event_time.isoformat(timespec="seconds"),
                    "eventType": event.get("eventType", ""),
                    "details": event.get("details", {}),
                }
            )

    return sorted(events, key=lambda item: item["time"], reverse=True)


def report_window(hours):
    end_time = now_local()
    start_time = end_time - timedelta(hours=int(hours))
    return start_time, end_time


def build_activity_report(
    activity_dir=DEFAULT_ACTIVITY_DIR,
    lock_events_dir=DEFAULT_LOCK_EVENTS_DIR,
    hours=12,
    temp_dir=None,
):
    start_time, end_time = report_window(hours)
    activity_dir = Path(activity_dir)
    temp_dir = Path(temp_dir or activity_dir / "tmp")
    temp_dir.mkdir(parents=True, exist_ok=True)

    app_events = [
        event
        for event in load_jsonl_dir(activity_dir / "app-usage")
        if event.get("timestamp") and datetime.fromisoformat(event["timestamp"]) >= start_time
    ]

    return {
        "generatedAt": end_time.isoformat(timespec="seconds"),
        "period": {
            "start": start_time.isoformat(timespec="seconds"),
            "end": end_time.isoformat(timespec="seconds"),
            "hours": int(hours),
        },
        "appsUsed": summarize_app_usage(app_events),
        "browserHistory": read_browser_history(start_time, temp_dir),
        "lockEvents": load_lock_events(lock_events_dir, start_time),
    }


def write_report(output_path, report):
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description="Monitor and report Gili's computer activity.")
    parser.add_argument("--mode", choices=("monitor", "report"), default="report")
    parser.add_argument("--activity-dir", default=str(DEFAULT_ACTIVITY_DIR))
    parser.add_argument("--lock-events-dir", default=str(DEFAULT_LOCK_EVENTS_DIR))
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT_PATH))
    parser.add_argument("--mobile-output", default="")
    parser.add_argument("--interval-seconds", type=int, default=30)
    parser.add_argument("--hours", type=int, default=12)
    args = parser.parse_args()

    if args.mode == "monitor":
        monitor(args.activity_dir, args.interval_seconds)
        return

    report = build_activity_report(args.activity_dir, args.lock_events_dir, args.hours)
    write_report(args.output, report)
    if args.mobile_output:
        write_report(args.mobile_output, report)
    print(f"Wrote activity report: {args.output}")
    if args.mobile_output:
        print(f"Wrote mobile activity report: {args.mobile_output}")


if __name__ == "__main__":
    main()
