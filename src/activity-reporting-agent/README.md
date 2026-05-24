# Activity Reporting Agent

Separate side agent for parent activity reporting.

Responsibilities:

- Sample the active app/window while the child is logged in.
- Read recent browser history from Chrome, Edge, and Firefox when generating a report.
- Include lock events from the existing locker event log.
- Write a simple JSON report for the mobile app.

This agent must stay separate from the locker. If reporting fails, locking should continue normally.

## Generate Report

```powershell
python .\activity_reporter.py --mode report
```

Default report output:

```text
C:\ProgramData\Cultural Aspects\activity-report.json
```

## Monitor Apps

```powershell
pythonw .\activity_reporter.py --mode monitor
```

The monitor is intended to run from a scheduled task in the child user's session.
