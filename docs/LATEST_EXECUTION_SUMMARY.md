# Latest Execution Summary

Last updated: 2026-05-24

This file summarizes the latest completed project work and can be used as a reference for future features.

## GitHub Authentication and Push

- Git Credential Manager was authenticated as GitHub user `ozcarmel`.
- The repository remote is:
  - `https://github.com/ozcarmel/computer-locker.git`
- The baseline project was pushed to GitHub.
- Current pushed commits:
  - `d49a016 Create cultural aspects baseline`
  - `746b6d1 Fix scheduled task run level`

## Stable Baseline

- All 10 planned project steps were implemented.
- The project was committed locally and pushed to GitHub.
- Main recovery/reference files:
  - `PROJECT_REFERENCE.md`
  - `AGENTS.md`
  - `docs\DEVELOPMENT_STEPS.md`
  - `docs\INSTALL_AND_RECOVERY.md`
  - `docs\END_TO_END_TESTING.md`

## Windows App

- The Windows lock app prototype is located at:
  - `src\windows-lock-app`
- The packaged executable name is:
  - `cultural-aspects.exe`
- Expected executable path:
  - `C:\Cultural Aspects\src\windows-lock-app\dist\cultural-aspects.exe`
- The app includes:
  - 20-minute work/break logic.
  - Full-screen regular break lock screen.
  - Parent password field on the regular break lock screen to finish the countdown early.
  - Daily usage limit lock screen.
  - Parent password override.
  - Parent-added extra time cap.
  - Local reporting event logs.
  - Parent-password protection for test lock and exit.

## Mobile Reporting App

- The mobile reporting app prototype is located at:
  - `src\mobile-reporting-app`
- It is a static mobile-friendly web app.
- It can load:
  - `report-data.json`
  - manually selected report JSON files
- It displays:
  - total usage time
  - total lock screens
  - report days
  - daily usage by date
  - regular lock appearances
  - daily-limit lock appearances
  - parent extra time
  - test locks

## Reporting Data

- Runtime event files are written under:
  - `C:\Cultural Aspects\data\events\YYYY-MM-DD.jsonl`
- Runtime data is ignored by Git.
- Report export command:

```powershell
Set-Location -LiteralPath 'C:\Cultural Aspects\src\windows-lock-app'
python .\generate_report.py --output ..\mobile-reporting-app\report-data.json
```

## Packaging

- Release package script:
  - `scripts\package\create_release_package.ps1`
- Release package output:
  - `C:\Cultural Aspects\release\cultural-aspects-baseline.zip`
- The release package includes:
  - `cultural-aspects.exe`
  - mobile reporting app files
  - admin scripts
  - build and test scripts
  - documentation
- The release package excludes:
  - runtime usage data
  - logs
  - local secrets
  - build cache folders

## Admin Startup Task

- The scheduled task was installed successfully.
- Task name:
  - `ComputerLocker-ChildLogon`
- Trigger:
  - at logon for `FBI\gilic`
- Task state after installation:
  - `Ready`
- Task action:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File "C:\Cultural Aspects\scripts\admin\launch_lock_app.ps1" -ProjectRoot "C:\Cultural Aspects"
```

- The launcher prefers:
  - `C:\Cultural Aspects\src\windows-lock-app\dist\cultural-aspects.exe`
- If the executable is missing, it falls back to Python.
- The task uses:
  - `RunLevel Limited`
  - `LogonType Interactive`

## Source Hiding Plan

- The child account can currently see the source project if it can browse `C:\Cultural Aspects`.
- The safer structure is:
  - runtime app under `C:\Program Files\Cultural Aspects`
  - runtime logs/data under `C:\ProgramData\Cultural Aspects`
  - source project hidden/protected from the child account
- Added scripts:
  - `scripts\admin\install_protected_runtime.ps1`
  - `scripts\admin\protect_source_folder.ps1`

## Important Compatibility Fix

- The first scheduled-task installation failed because this Windows version did not accept:
  - `RunLevel LeastPrivilege`
- The script was fixed to use:
  - `RunLevel Limited`
- The fix was committed and pushed:
  - `746b6d1 Fix scheduled task run level`

## How to Confirm Startup

After signing out and signing back in to `FBI\gilic`, confirm:

1. A window titled `Computer Locker - Parent Controls` appears.
2. Task Manager shows:
   - `cultural-aspects.exe`
3. Task Scheduler shows a recent run for:
   - `ComputerLocker-ChildLogon`
4. Runtime events later appear under:
   - `C:\Cultural Aspects\data\events`

## Useful Commands

Run automated checks:

```powershell
Set-Location -LiteralPath 'C:\Cultural Aspects'
.\scripts\test\run_e2e_checks.ps1 -SkipBuild
```

Rebuild executable:

```powershell
Set-Location -LiteralPath 'C:\Cultural Aspects'
.\scripts\build\build_windows_exe.ps1
```

Recreate release package:

```powershell
Set-Location -LiteralPath 'C:\Cultural Aspects'
.\scripts\package\create_release_package.ps1
```

Remove startup task:

```powershell
Set-Location -LiteralPath 'C:\Cultural Aspects'
.\scripts\admin\uninstall_startup_task.ps1
```

## Future Feature Hooks

Potential future additions:

- Stronger anti-bypass controls using Windows policy.
- Watchdog or Windows service support.
- Secure parent password setup and storage.
- Automatic report sync to the parent's phone.
- Cloud-backed mobile reporting.
- Notifications when daily limit is reached.
- Parent settings UI.
- Multiple child account support.
- Real installer under `C:\Program Files`.
- Better app icon and signed executable.
- Microsoft Family Safety integration.
