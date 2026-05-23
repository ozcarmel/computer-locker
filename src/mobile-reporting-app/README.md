# Mobile Reporting App

This folder contains the parent-facing mobile reporting app prototype.

Current responsibilities:

- Show daily logged-in computer usage hours.
- Show when lock screens appeared during the day.
- Organize reports by date.
- Keep the report simple and readable.
- Load exported report JSON from the Windows lock app.
- Work as a static mobile-friendly web app.

## Run Locally

From this folder:

```powershell
python -m http.server 8088
```

Open:

```text
http://127.0.0.1:8088
```

## Export Report Data

From the Windows lock app folder:

```powershell
python .\generate_report.py --output ..\mobile-reporting-app\report-data.json
```

The mobile app will load `report-data.json` automatically when it exists. It also supports manually selecting a report JSON file.
