# End-to-End Testing

Step 9 defines repeatable checks for the current project.

## Automated Checks

Run from PowerShell:

```powershell
Set-Location -LiteralPath 'C:\Cultural Aspects'
.\scripts\test\run_e2e_checks.ps1
```

To skip rebuilding `cultural-aspects.exe`:

```powershell
.\scripts\test\run_e2e_checks.ps1 -SkipBuild
```

The automated checks verify:

- Python unit tests pass.
- PowerShell setup scripts parse correctly.
- `cultural-aspects.exe` exists or can be rebuilt.
- Report JSON can be exported.
- Exported report JSON is valid.
- Mobile reporting app files exist.
- Scheduled-task cmdlets required by the admin setup script are available.

## Manual UI Smoke Test

Use short intervals so the test is quick:

```powershell
Set-Location -LiteralPath 'C:\Cultural Aspects\src\windows-lock-app'
$env:LOCK_APP_WORK_SECONDS = '5'
$env:LOCK_APP_BREAK_SECONDS = '3'
$env:LOCK_APP_DAILY_LIMIT_SECONDS = '10'
$env:LOCK_APP_PARENT_EXTRA_SECONDS_LIMIT = '20'
$env:LOCK_APP_PARENT_PASSWORD = 'parent'
.\dist\cultural-aspects.exe
```

Expected behavior:

1. The parent control window opens.
2. After 5 seconds, the regular lock screen appears.
3. After 3 seconds, the timer reaches `00:00`.
4. Spacebar releases the regular lock screen.
5. After the second 5-second work interval, the daily-limit screen appears.
6. Spacebar does not close the daily-limit screen.
7. Entering the parent password grants extra time.
8. Parent exit requires the parent password.

## Admin Startup Test

This test requires an elevated Administrator PowerShell window.

```powershell
Set-Location -LiteralPath 'C:\Cultural Aspects'
.\scripts\admin\install_startup_task.ps1 -ChildUsername 'FBI\gilic'
```

Then:

1. Sign out of the child account.
2. Sign back in to the child account.
3. Confirm `cultural-aspects.exe` starts automatically.
4. Confirm the parent control window appears.
5. Run a short work/break test if needed.

To remove the task:

```powershell
Set-Location -LiteralPath 'C:\Cultural Aspects'
.\scripts\admin\uninstall_startup_task.ps1
```

## Mobile Report Test

Export report data:

```powershell
Set-Location -LiteralPath 'C:\Cultural Aspects\src\windows-lock-app'
python .\generate_report.py --output ..\mobile-reporting-app\report-data.json
```

Serve the mobile report locally:

```powershell
Set-Location -LiteralPath 'C:\Cultural Aspects\src\mobile-reporting-app'
python -m http.server 8088
```

Open:

```text
http://127.0.0.1:8088
```

Expected behavior:

- The mobile app loads.
- Daily report cards are shown when report data exists.
- Empty state is shown when no report data exists.
- The file picker can load a report JSON file.

## Not Yet Automated

- Real child login/relogin behavior.
- Running after reboot.
- Task Scheduler recovery if the app is killed.
- Strong anti-bypass policy behavior.

Those require administrator setup and real Windows session testing.
