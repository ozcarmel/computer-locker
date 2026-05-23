# Windows Lock App

This folder contains the Windows desktop lock-screen prototype.

Current Step 2 prototype responsibilities:

- Display a parent control window.
- Provide a `Test Lock Screen` button.
- Display a full-screen regular break lock screen.
- Show the message: "Computer is locked for 20 min. Take a break"
- Show a countdown timer starting at `20:00`.
- Keep the lock screen visible at `00:00` until the spacebar is pressed.
- Allow parent password on the regular lock screen to set the timer to `00:00`.

Current Step 3 prototype responsibilities:

- Start a work interval automatically when the app opens.
- Track unlocked usage for the current day.
- Trigger the regular break lock when the work interval reaches `00:00`.
- Count completed work cycles.
- Detect the 2-hour daily limit internally.
- Reset the daily allowance at 8:00.

Current Step 4 prototype responsibilities:

- Show the daily-limit lock screen when the daily usage limit is reached.
- Show the message: "you've reached the limit usage for today. Try again tomorrow"
- Ignore spacebar and common close shortcuts on the daily-limit screen.
- Show a parent password field.
- Add 20 minutes of extra time after the correct parent password is entered.
- Limit parent-added time to 1 hour per day.
- Reset the daily limit and parent extra time at 8:00.

Current Step 5 prototype responsibilities:

- Write local JSONL event files under `data\events`.
- Record completed unlocked usage intervals.
- Record regular lock appearances and releases.
- Record daily-limit lock appearances.
- Record parent extra-time grants.
- Record test-lock button usage.
- Generate a simple daily summary for future mobile reporting.

Current Step 7 prototype responsibilities:

- Require the parent password before testing the lock screen.
- Require the parent password before exiting the app.
- Prevent casual closing through the window close button and Alt+F4.
- Log denied parent actions and authorized parent exits.
- Allow parent password to finish the regular break countdown early.

Not implemented yet:

- Scheduled startup.
- Strong administrator-policy hardening.

## Run

From this folder:

```powershell
python .\app.py
```

## Build Executable

From the project root:

```powershell
.\scripts\build\build_windows_exe.ps1
```

The executable name must be:

```text
cultural-aspects.exe
```

For a short local test countdown:

```powershell
$env:LOCK_APP_BREAK_SECONDS = "5"
python .\app.py
```

For a short automatic work/break cycle test:

```powershell
$env:LOCK_APP_WORK_SECONDS = "5"
$env:LOCK_APP_BREAK_SECONDS = "5"
$env:LOCK_APP_DAILY_LIMIT_SECONDS = "30"
python .\app.py
```

For a short daily-limit and parent override test:

```powershell
$env:LOCK_APP_WORK_SECONDS = "5"
$env:LOCK_APP_BREAK_SECONDS = "3"
$env:LOCK_APP_DAILY_LIMIT_SECONDS = "10"
$env:LOCK_APP_PARENT_EXTRA_SECONDS_LIMIT = "20"
$env:LOCK_APP_PARENT_PASSWORD = "parent"
python .\app.py
```

Prototype note: if `LOCK_APP_PARENT_PASSWORD` is not set, the temporary prototype password is `parent`. Production code must replace this with secure password setup and storage.

## Test

```powershell
python -m unittest discover -s tests
```

## Generate Local Report

```powershell
python .\generate_report.py
```

The report summarizes daily unlocked usage seconds, regular lock appearances, daily-limit lock appearances, parent extra time, and test-lock appearances.
