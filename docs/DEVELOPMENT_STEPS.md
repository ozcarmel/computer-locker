# Development Steps

This project is developed one approved step at a time. After each step is ready, work pauses for parent approval before continuing.

## Step 1: Project Foundation

Status: Approved

Goal:

- Create the repository structure.
- Add starter documentation.
- Add example configuration.
- Create places for source code, admin setup scripts, runtime data, and logs.

Approval required before Step 2 begins.

## Step 2: Lock Screen Prototype

Status: Approved

Goal:

- Build the first full-screen lock window.
- Show the regular break message.
- Show a `20:00` countdown timer.
- Keep the lock visible at `00:00` until the spacebar is pressed.
- Add an immediate test-lock path.

Implemented:

- Added a Python/Tkinter prototype under `src\windows-lock-app`.
- Added a parent control window with a `Test Lock Screen` button.
- Added a full-screen, topmost regular break lock screen.
- Added countdown formatting and timer helpers.
- Added unit tests for countdown behavior.

## Step 3: Usage Timer Logic

Status: Approved

Goal:

- Track unlocked usage time.
- Trigger a lock every 20 minutes.
- Count six work cycles.
- Detect the 2-hour daily limit.
- Reset the daily allowance at 8:00.

Implemented:

- Added a usage timer engine under `src\windows-lock-app`.
- Added automatic work interval startup.
- Added automatic break triggering when the work interval reaches zero.
- Added completed-cycle tracking.
- Added internal daily-limit detection.
- Added daily reset logic for 8:00.
- Added short-test environment variables for work, break, and daily-limit durations.
- Added unit tests for usage timer behavior.

## Step 4: Daily Limit Lock

Status: Approved

Goal:

- Add the daily-limit lock screen.
- Add parent password override.
- Limit parent-added time to 1 hour per day.

Implemented:

- Added a daily-limit full-screen lock screen.
- Added the daily-limit message.
- Added parent password input.
- Added parent extra-time grants in 20-minute increments.
- Limited parent-added time to 1 hour per day.
- Added daily reset of parent-added time at 8:00.
- Added unit tests for parent extra-time behavior.

## Step 5: Local Reporting Data

Status: Approved

Goal:

- Record usage and lock events locally.
- Prepare data for the mobile reporting app.

Implemented:

- Added local JSONL event logging under `data\events`.
- Added event records for app start, completed usage intervals, regular locks, lock releases, daily-limit locks, parent extra-time grants, and test locks.
- Added a daily summary builder for future mobile reporting.
- Added a report generator command.
- Added unit tests for event logging and daily report summaries.

## Step 6: Admin Startup Setup

Status: Approved

Goal:

- Add administrator setup scripts.
- Create scheduled task or startup behavior.
- Ask for administrator elevation when needed.

Implemented:

- Added administrator-run scheduled task install script.
- Added scheduled task removal script.
- Added launcher script used by the scheduled task.
- Added admin startup setup documentation.
- Documented why the visible lock app must run in the child user's interactive session.
- Validated PowerShell script syntax without installing the task.

## Step 7: Hardening

Status: Approved

Goal:

- Make the app harder for a standard user to bypass.
- Consider Windows policy, scheduled task restart behavior, or service support.

Implemented:

- Added parent password verification helper.
- Protected parent control window close behavior.
- Protected Alt+F4 on the parent control window.
- Added parent-password requirement for test lock.
- Added parent-password requirement for app exit.
- Logged denied parent actions and authorized parent exits.
- Added hardening documentation and remaining limitations.

## Step 8: Mobile Reporting App

Status: Approved

Goal:

- Build the parent-facing mobile reporting app.
- Show daily usage hours and lock events by date.

Implemented:

- Added a static mobile-friendly reporting app under `src\mobile-reporting-app`.
- Added daily summary cards by date.
- Added summary totals for usage time, lock screens, and report days.
- Added report JSON file import.
- Added automatic loading of `report-data.json` when available.
- Added PWA manifest and service worker.
- Added report export support to the Windows report generator.

## Step 9: End-to-End Testing

Status: Approved

Goal:

- Test startup, locking, limits, override, reporting, restart, and relogin behavior.

Implemented:

- Added automated end-to-end check script.
- Added manual UI smoke-test checklist.
- Added admin startup test checklist.
- Added mobile report test checklist.
- Documented what still requires real admin/login testing.

## Step 10: Package and Recovery

Status: Ready for approval

Goal:

- Add install instructions.
- Update recovery documentation.
- Create a stable Git baseline.

Implemented:

- Added install and recovery documentation.
- Added local release packaging script.
- Added release folder and zip output policy.
- Prepared the repository for the first stable Git baseline.
