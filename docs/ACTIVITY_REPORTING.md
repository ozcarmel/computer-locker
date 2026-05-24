# Activity Reporting

The activity reporter is a separate side agent. It does not run inside the locker app.

## What It Records

- Active app/window samples while the child is logged in.
- Recent browser history from Chrome, Edge, and Firefox.
- Lock events from the existing locker event log.

## Runtime Files

Runtime data is written under:

```text
C:\ProgramData\Cultural Aspects
```

Main report file:

```text
C:\ProgramData\Cultural Aspects\activity-report.json
```

Mobile app copy:

```text
C:\Cultural Aspects\src\mobile-reporting-app\activity-report.json
```

OneDrive sync folder:

```text
C:\Users\gilic\OneDrive\Gili Activity Report
```

## Install Scheduled Tasks

Run from an elevated Administrator PowerShell window:

```powershell
Set-Location -LiteralPath 'C:\Cultural Aspects'
.\scripts\admin\install_activity_reporter_tasks.ps1 -ChildUsername 'FBI\gilic'
```

Installed tasks:

- `CulturalAspects-ActivityMonitor` starts after `FBI\gilic` logs in.
- `CulturalAspects-ActivityReport` generates reports twice per day at 8:00 and 20:00.

## Generate A Report Manually

```powershell
Set-Location -LiteralPath 'C:\Cultural Aspects\src\activity-reporting-agent'
python .\activity_reporter.py --mode report --output 'C:\ProgramData\Cultural Aspects\activity-report.json' --mobile-output 'C:\Cultural Aspects\src\mobile-reporting-app\activity-report.json'
```

## Phone Access

Serve the mobile app from the computer:

```powershell
Set-Location -LiteralPath 'C:\Cultural Aspects\src\mobile-reporting-app'
python -m http.server 8088
```

Open the computer's LAN IP address from the phone:

```text
http://<computer-ip>:8088
```

## OneDrive Sync

The activity report task also copies the mobile app files and latest JSON reports into:

```text
C:\Users\gilic\OneDrive\Gili Activity Report
```

Share that OneDrive folder privately with the parent who should read the reports.
