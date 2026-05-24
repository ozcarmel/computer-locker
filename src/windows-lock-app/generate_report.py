import json
import argparse
from pathlib import Path

from reporting import build_daily_report, build_event_report, load_events


def main():
    parser = argparse.ArgumentParser(description="Generate the daily Computer Locker report.")
    parser.add_argument(
        "--output",
        help="Optional path to write the report JSON.",
    )
    parser.add_argument(
        "--events-dir",
        help="Optional event-log directory. Defaults to LOCK_APP_EVENTS_DIR or the project data folder.",
    )
    parser.add_argument(
        "--format",
        choices=("json", "text"),
        default="json",
        help="Report format. Use text for a readable parent-facing event report.",
    )
    args = parser.parse_args()

    events = load_events(args.events_dir)
    if args.format == "text":
        content = build_event_report(events)
    else:
        report = build_daily_report(events)
        content = json.dumps(report, indent=2, sort_keys=True) + "\n"

    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(content, encoding="utf-8")
        print(f"Wrote report: {output_path}")
        return

    print(content, end="")


if __name__ == "__main__":
    main()
