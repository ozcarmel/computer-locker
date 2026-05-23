import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


class GenerateReportTests(unittest.TestCase):
    def test_generate_report_can_write_output_file(self):
        app_dir = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as directory:
            output_path = Path(directory) / "report.json"
            result = subprocess.run(
                [
                    sys.executable,
                    str(app_dir / "generate_report.py"),
                    "--output",
                    str(output_path),
                ],
                cwd=app_dir,
                env={**os.environ, "LOCK_APP_EVENTS_DIR": str(Path(directory) / "events")},
                text=True,
                capture_output=True,
                check=True,
            )

            self.assertIn("Wrote report:", result.stdout)
            self.assertEqual(json.loads(output_path.read_text(encoding="utf-8")), {})


if __name__ == "__main__":
    unittest.main()
