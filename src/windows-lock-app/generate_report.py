import json
import argparse
from pathlib import Path

from reporting import build_daily_report, load_events


def main():
    parser = argparse.ArgumentParser(description="Generate the daily Computer Locker report.")
    parser.add_argument(
        "--output",
        help="Optional path to write the report JSON.",
    )
    args = parser.parse_args()

    report = build_daily_report(load_events())
    content = json.dumps(report, indent=2, sort_keys=True)

    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(content + "\n", encoding="utf-8")
        print(f"Wrote report: {output_path}")
        return

    print(content)


if __name__ == "__main__":
    main()
