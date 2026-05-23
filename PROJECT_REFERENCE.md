# Cultural Aspects Project Reference

Last updated: 2026-05-24

This file is the stable project baseline. Use it as a reference for future development and as a recovery point if the project direction, app structure, or agent instructions become unclear.

## Project Location

- Active project folder: `C:\Cultural Aspects`
- Previous source folder: `C:\Users\gilic\OneDrive\Documents\computer lock and report`
- GitHub account: `https://github.com/ozcarmel`
- GitHub repository: `https://github.com/ozcarmel/computer-locker.git`
- Git repository status at setup: initialized, no commits yet
- Active project instruction file: `AGENTS.md`

## Project Goal

Build a Windows computer-locking and reporting system for a child standard Windows account.

The system should:

- Run whenever the computer is on.
- Run whenever a standard user account logs in to Windows on this computer.
- Be created, installed, configured, and scheduled through the parent/admin account when elevated permissions are required.
- Enforce timed computer breaks and a daily usage limit for the child account.
- Provide a parent override flow.
- Provide a simple mobile reporting app for the parent.

## Development Context

- Development is currently being done from the child's standard Windows account.
- The parent has an administrator account and knows the administrator password.
- If admin permissions are needed, development should pause and clearly ask for administrator elevation.
- Admin elevation may be needed for:
  - Installing the app into protected locations such as `C:\Program Files`.
  - Creating system-level scheduled tasks.
  - Configuring scheduled tasks to run under the Admin account.
  - Configuring startup behavior for all users or for standard-user login.
  - Applying Windows restrictions that prevent a standard user from closing or disabling the app.

## Project Agents

### Agent: Use administrator account

Purpose:

- Ensure the app and scheduled tasks are run through the Admin account when required.

Rules:

- Always use the Admin account to run the application created for this project.
- Always use the Admin account when creating, configuring, or running scheduled tasks for this project.
- Scheduled tasks must run automatically when non-admin users are logged in.
- Non-admin users should not need to manually launch privileged project tasks.
- Credentials, secrets, and account-specific configuration must stay out of source control.

### Agent: Locking mechanism

Purpose:

- Define the locking mechanism, timing rules, lock-screen behavior, parent override behavior, and test-lock behavior.

Rules:

- When a standard account is using the computer, the computer is locked every 20 minutes.
- Each regular lock period lasts 20 minutes.
- When locked, a lock screen appears.
- Regular lock message: "Computer is locked for 20 min. Take a break"
- The lock screen shows a descending timer starting at `20:00` in minutes:seconds format.
- After 20 minutes, the timer shows `00:00`, but the lock screen remains until the user presses the spacebar.
- Daily unlocked usage is limited to 2 hours.
- The 2-hour limit equals six 20-minute unlocked usage cycles.
- After the daily limit is reached, show this message: "you've reached the limit usage for today. Try again tomorrow"
- The daily-limit lock screen remains until the next day at 8:00.
- The daily-limit lock screen should not be removable or manipulable by keyboard keys or keyboard shortcuts.
- The daily-limit lock screen includes a parent password window.
- A parent can enter the password to unlock and add usage time.
- Parent-added usage time is limited to a maximum of 1 additional hour per day.
- A test button allows the parent to immediately show the lock screen at any time.

Important implementation note:

- A normal Windows desktop app can be made difficult for a standard user to close, especially with admin-installed startup and account restrictions. However, Windows security shortcuts and system-level controls may still exist. Strong enforcement may require Windows Task Scheduler, a Windows service, kiosk-style restrictions, Group Policy, or Microsoft Family Safety-style controls.

### Agent: Mobile reporting app

Purpose:

- Define and maintain a simple parent-facing mobile reporting app.

Rules:

- The mobile app reports the child's daily logged-in computer usage hours.
- The mobile app reports when the screen lock appeared during the day.
- Reports are organized by date.
- Reports are simple, readable, and parent-facing.

## Planned Application Architecture

Recommended starting architecture:

- Windows desktop lock app:
  - Runs in the child user's interactive session.
  - Displays the full-screen lock overlay.
  - Tracks active unlocked usage time.
  - Shows break and daily-limit lock screens.
  - Provides parent override and test lock controls.

- Admin/scheduler setup:
  - Uses administrator elevation.
  - Creates startup or login scheduled tasks.
  - Ensures the app starts when the child standard user logs in.
  - May later install a background service if stronger monitoring is needed.

- Local data store:
  - Stores usage sessions, lock events, break periods, daily-limit events, and parent overrides.
  - Keeps parent password hashes and secrets out of source control.

- Reporting/mobile side:
  - Reads or syncs daily report data from the Windows app.
  - Shows daily logged-in usage hours and lock events.
  - Exact sync method is not yet chosen.

## Implemented Project Foundation

Step 1 created the initial repository structure:

- `README.md` - project overview and folder map.
- `.gitignore` - excludes runtime data, logs, local configuration, secrets, and build outputs.
- `config\appsettings.example.json` - example non-secret configuration.
- `data` - placeholder folder for future local runtime data.
- `logs` - placeholder folder for future runtime logs.
- `docs\DEVELOPMENT_STEPS.md` - step-by-step approval workflow.
- `src\windows-lock-app` - placeholder for the future Windows locking app.
- `src\mobile-reporting-app` - placeholder for the future mobile reporting app.
- `scripts\admin` - placeholder for future administrator setup scripts.

## Implemented Lock Screen Prototype

Step 2 added the first Windows lock-screen prototype:

- `src\windows-lock-app\app.py` - parent control window with a `Test Lock Screen` button.
- `src\windows-lock-app\lock_screen.py` - full-screen regular break lock screen.
- `src\windows-lock-app\countdown.py` - countdown formatting and remaining-time helpers.
- `src\windows-lock-app\tests\test_countdown.py` - unit tests for countdown behavior.

The prototype uses Python/Tkinter because Python is available on the current standard account. The installed .NET runtime is present, but no .NET SDK is available in the current environment.

Current prototype behavior:

- Shows the regular break message.
- Shows a timer starting at `20:00`.
- Leaves the lock screen visible when the timer reaches `00:00`.
- Allows spacebar release only after the timer reaches `00:00`.
- Supports short test runs with the `LOCK_APP_TEST_SECONDS` environment variable.

## Implemented Usage Timer Logic

Step 3 added internal usage timing:

- `src\windows-lock-app\usage_timer.py` - usage timer state and daily reset logic.
- `src\windows-lock-app\tests\test_usage_timer.py` - unit tests for work intervals, cycle counts, daily limit detection, and 8:00 reset behavior.

Current timer behavior:

- Starts an unlocked work interval when the app opens.
- Tracks unlocked usage time for the current day.
- Triggers a regular break lock when the work interval reaches zero.
- Counts completed work cycles.
- Detects the 2-hour daily limit internally.
- Resets daily usage at 8:00.

Short test environment variables:

- `LOCK_APP_WORK_SECONDS` - override the work interval duration.
- `LOCK_APP_BREAK_SECONDS` - override the break lock duration.
- `LOCK_APP_DAILY_LIMIT_SECONDS` - override the daily limit duration.

## Implemented Daily Limit Lock

Step 4 added the daily-limit lock behavior:

- `src\windows-lock-app\daily_limit_screen.py` - full-screen daily-limit lock screen.
- The daily-limit message is shown when the daily usage limit is reached.
- Spacebar and common close shortcuts are ignored on the daily-limit screen.
- A parent password field is shown on the daily-limit screen.
- Correct parent password grants 20 minutes of extra unlocked time.
- Parent-added time is capped at 1 additional hour per day.
- Daily usage and parent-added time reset at 8:00.

Prototype password behavior:

- The parent password is read from the `LOCK_APP_PARENT_PASSWORD` environment variable.
- If the variable is not set, the temporary prototype password is `parent`.
- Production code must replace this with secure password setup and storage.

Short daily-limit test variables:

- `LOCK_APP_WORK_SECONDS` - short work interval.
- `LOCK_APP_BREAK_SECONDS` - short break interval.
- `LOCK_APP_DAILY_LIMIT_SECONDS` - short daily limit.
- `LOCK_APP_PARENT_EXTRA_SECONDS_LIMIT` - short parent extra limit.
- `LOCK_APP_PARENT_PASSWORD` - prototype parent password.

## Implemented Local Reporting Data

Step 5 added local reporting data:

- `src\windows-lock-app\reporting.py` - JSONL event logger and daily summary builder.
- `src\windows-lock-app\generate_report.py` - command-line daily report generator.
- `src\windows-lock-app\tests\test_reporting.py` - unit tests for reporting behavior.

Runtime event files are written under:

- `data\events\YYYY-MM-DD.jsonl`

Recorded event types include:

- `app_started`
- `usage_interval_completed`
- `regular_lock_started`
- `regular_lock_released`
- `daily_limit_lock_started`
- `parent_extra_time_granted`
- `test_lock_started`

The daily summary currently includes:

- Daily unlocked usage seconds.
- Regular lock appearances.
- Daily-limit lock appearances.
- Parent extra seconds granted.
- Test-lock appearances.

Runtime event files are ignored by Git through `.gitignore`.

## Implemented Admin Startup Setup

Step 6 added administrator startup setup files:

- `scripts\admin\install_startup_task.ps1` - creates or updates the scheduled task.
- `scripts\admin\launch_lock_app.ps1` - launcher used by the scheduled task.
- `scripts\admin\uninstall_startup_task.ps1` - removes the scheduled task.
- `scripts\build\build_windows_exe.ps1` - builds the Windows executable.
- `docs\ADMIN_STARTUP_SETUP.md` - setup and removal instructions.

Important Windows behavior:

- The administrator account creates and manages the scheduled task.
- The visible lock-screen app must run in the child user's interactive desktop session, otherwise Windows session isolation can prevent the lock window from appearing to the child.
- The current setup therefore creates a child-logon scheduled task managed from an elevated Administrator PowerShell window.

Default scheduled task name:

- `ComputerLocker-ChildLogon`

Install command:

```powershell
Set-Location -LiteralPath 'C:\Cultural Aspects'
.\scripts\admin\install_startup_task.ps1 -ChildUsername 'FBI\gilic'
```

Removal command:

```powershell
Set-Location -LiteralPath 'C:\Cultural Aspects'
.\scripts\admin\uninstall_startup_task.ps1
```

The scheduled task has not been installed yet. It requires an elevated Administrator PowerShell window.

Production executable name:

- `cultural-aspects.exe`

Expected executable path after build:

- `src\windows-lock-app\dist\cultural-aspects.exe`

The scheduled-task launcher prefers `cultural-aspects.exe` when it exists and falls back to the Python prototype only when the executable has not been built yet.

The scheduled task uses `RunLevel Limited`, which is the Windows ScheduledTasks enum for least-privileged interactive execution on this machine.

## Implemented Prototype Hardening

Step 7 added practical prototype hardening:

- `src\windows-lock-app\parent_auth.py` - parent password verification helper.
- `src\windows-lock-app\tests\test_parent_auth.py` - unit tests for parent password verification.
- `docs\HARDENING_NOTES.md` - hardening behavior, limitations, and future options.

Current hardening behavior:

- Closing the parent control window requires the parent password.
- Alt+F4 on the parent control window requires the parent password.
- The test lock button requires the parent password.
- The parent exit button requires the parent password.
- Incorrect parent-password attempts are logged.
- Authorized parent exits are logged.

Current hardening limits:

- This is still a user-mode Python prototype.
- A determined standard user may still attempt to kill the process, interfere with files, or use Windows system-level controls.
- Stronger hardening will require administrator-controlled install location, Windows policy, Task Scheduler restart behavior, or a service/watchdog design.

## Implemented Mobile Reporting App

Step 8 added the parent-facing mobile reporting app prototype:

- `src\mobile-reporting-app\index.html` - mobile report UI.
- `src\mobile-reporting-app\styles.css` - responsive mobile styling.
- `src\mobile-reporting-app\app.js` - report loading and rendering.
- `src\mobile-reporting-app\manifest.webmanifest` - PWA manifest.
- `src\mobile-reporting-app\service-worker.js` - offline app shell cache.
- `src\mobile-reporting-app\report-data.sample.json` - sample report data.

The Windows report generator now supports:

```powershell
python .\generate_report.py --output ..\mobile-reporting-app\report-data.json
```

The mobile app displays:

- Total usage time.
- Total lock screens.
- Number of report days.
- Daily usage by date.
- Regular lock appearances by date.
- Daily-limit lock appearances by date.
- Parent extra time by date.
- Test locks by date.

Current sync model:

- Manual JSON export/import.
- The app automatically loads `report-data.json` when available.
- Parent can also select a JSON file manually.

## Implemented End-to-End Testing

Step 9 added end-to-end testing support:

- `scripts\test\run_e2e_checks.ps1` - automated project checks.
- `docs\END_TO_END_TESTING.md` - manual and admin test checklist.

Automated checks cover:

- Python unit tests.
- PowerShell script syntax.
- `cultural-aspects.exe` build/existence.
- Report JSON export and validation.
- Mobile reporting app file presence.
- Scheduled-task cmdlet compatibility.

Manual checks document:

- Short-interval lock app UI smoke test.
- Admin scheduled-task install/login test.
- Mobile report export and local viewing test.

Real child relogin, reboot behavior, and strong anti-bypass behavior still require administrator setup and manual Windows session testing.

## Implemented Package and Recovery

Step 10 added package and recovery support:

- `scripts\package\create_release_package.ps1` - creates a local release folder and zip package.
- `docs\INSTALL_AND_RECOVERY.md` - build, package, install, recovery, and data-safety instructions.
- `docs\LATEST_EXECUTION_SUMMARY.md` - latest execution summary for future feature planning.

Package output:

- `release\cultural-aspects-baseline.zip`

The release package includes:

- `cultural-aspects.exe`
- Mobile reporting app files.
- Admin, build, and test scripts.
- Documentation and project reference files.

The release package excludes:

- Runtime event data.
- Logs.
- Local secrets.
- Build cache folders.

## Open Design Decisions

- Which Windows app technology to use.
- Whether the lock app should be a desktop app only, or desktop app plus Windows service.
- How parent password storage should be implemented.
- How mobile reporting will receive data:
  - Local network sync.
  - Cloud database.
  - Manual export.
  - Email or notification report.
- How strong the anti-bypass behavior needs to be.
- Whether to combine this custom app with Microsoft Family Safety or Windows policy restrictions.

## Recovery Instructions

If project files or instructions become confusing:

1. Return to `C:\Cultural Aspects`.
2. Read this file first.
3. Read `AGENTS.md` second.
4. Restore the core goals from the "Project Goal" section.
5. Restore agent behavior from the "Project Agents" section.
6. Rebuild implementation around the planned architecture above.

This file should be updated whenever the project direction, architecture, agents, or core rules change.
