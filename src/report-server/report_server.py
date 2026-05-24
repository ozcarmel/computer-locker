import argparse
import json
import os
import subprocess
import sys
import time
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
MOBILE_APP_DIR = PROJECT_ROOT / "src" / "mobile-reporting-app"
WINDOWS_APP_DIR = PROJECT_ROOT / "src" / "windows-lock-app"
ACTIVITY_AGENT_DIR = PROJECT_ROOT / "src" / "activity-reporting-agent"
RUNTIME_DIR = Path(os.environ.get("PROGRAMDATA", r"C:\ProgramData")) / "Cultural Aspects"
DEFAULT_CLOUD_DIR = Path(r"C:\Users\gilic\OneDrive\Gili Activity Report")

sys.path.insert(0, str(WINDOWS_APP_DIR))
sys.path.insert(0, str(ACTIVITY_AGENT_DIR))

from activity_reporter import build_activity_report, sync_mobile_app_to_cloud, write_report  # noqa: E402
from reporting import build_daily_report, load_events  # noqa: E402


def write_json(path, payload):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def refresh_reports():
    lock_events_dir = RUNTIME_DIR / "data" / "events"

    locker_report = build_daily_report(load_events(lock_events_dir))
    write_json(MOBILE_APP_DIR / "report-data.json", locker_report)
    sync_mobile_app_to_cloud(MOBILE_APP_DIR, DEFAULT_CLOUD_DIR)

    scheduled_task_started = False
    try:
        subprocess.run(
            ["schtasks", "/Run", "/TN", "CulturalAspects-ActivityReport"],
            check=True,
            capture_output=True,
            text=True,
        )
        scheduled_task_started = True
        time.sleep(5)
    except (OSError, subprocess.CalledProcessError):
        activity_report = build_activity_report(
            activity_dir=RUNTIME_DIR / "activity",
            lock_events_dir=lock_events_dir,
            hours=12,
        )
        write_report(RUNTIME_DIR / "activity-report.json", activity_report)
        write_report(MOBILE_APP_DIR / "activity-report.json", activity_report)

    return {
        "ok": True,
        "message": "Reports refreshed",
        "scheduledActivityReportStarted": scheduled_task_started,
        "lockerReport": str(MOBILE_APP_DIR / "report-data.json"),
        "activityReport": str(MOBILE_APP_DIR / "activity-report.json"),
        "cloudFolder": str(DEFAULT_CLOUD_DIR),
    }


class ReportRequestHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, directory=None, **kwargs):
        super().__init__(*args, directory=str(directory or MOBILE_APP_DIR), **kwargs)

    def do_POST(self):
        if self.path != "/api/refresh":
            self.send_error(404, "Not found")
            return

        try:
            payload = refresh_reports()
            body = json.dumps(payload).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        except Exception as error:  # noqa: BLE001
            body = json.dumps({"ok": False, "error": str(error)}).encode("utf-8")
            self.send_response(500)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()


def main():
    parser = argparse.ArgumentParser(description="Serve the Gili Activity mobile app.")
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8088)
    args = parser.parse_args()

    refresh_reports()

    server = ThreadingHTTPServer(
        (args.host, args.port),
        lambda *handler_args, **handler_kwargs: ReportRequestHandler(
            *handler_args,
            directory=MOBILE_APP_DIR,
            **handler_kwargs,
        ),
    )
    print(f"Serving Gili Activity at http://{args.host}:{args.port}")
    server.serve_forever()


if __name__ == "__main__":
    main()
