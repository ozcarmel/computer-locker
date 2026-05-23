# Admin Startup Setup

Step 6 prepares administrator-run setup scripts for starting the lock app automatically when the child standard user logs in.

## Important Windows Behavior

The lock screen is a visible desktop window. A visible desktop app must run in the logged-in user's interactive session.

Because of that:

- The administrator account creates and manages the scheduled task.
- The scheduled task starts when the child standard user logs in.
- The app process runs in the child user's interactive session so the full-screen lock window can appear.

This is different from a hidden admin background service. A service may be added later for stronger monitoring, but the visible lock screen still needs an interactive user-session component.

## Scripts

- `scripts\admin\install_startup_task.ps1` - creates or updates the scheduled task.
- `scripts\admin\launch_lock_app.ps1` - launches the Python lock app.
- `scripts\admin\uninstall_startup_task.ps1` - removes the scheduled task.
- `scripts\build\build_windows_exe.ps1` - builds `cultural-aspects.exe`.

## Build Executable

From a normal PowerShell window:

```powershell
Set-Location -LiteralPath 'C:\Cultural Aspects'
.\scripts\build\build_windows_exe.ps1
```

Expected output:

```text
C:\Cultural Aspects\src\windows-lock-app\dist\cultural-aspects.exe
```

When `cultural-aspects.exe` exists, the startup launcher uses it instead of `python.exe` or `pythonw.exe`.

## Install

Open PowerShell as Administrator and run:

```powershell
Set-Location -LiteralPath 'C:\Cultural Aspects'
.\scripts\admin\install_startup_task.ps1 -ChildUsername 'FBI\gilic'
```

Replace `FBI\gilic` with the child Windows account if different.

## Remove

Open PowerShell as Administrator and run:

```powershell
Set-Location -LiteralPath 'C:\Cultural Aspects'
.\scripts\admin\uninstall_startup_task.ps1
```

## Verify

After installation:

1. Sign out of the child account.
2. Sign back in to the child account.
3. The Computer Locker parent control window should open automatically.

You can also check Task Scheduler for:

```text
ComputerLocker-ChildLogon
```

The scheduled task is configured with `RunLevel Limited` so it runs in the child user's interactive session without requesting elevation for the child account.

## Current Limitations

- This setup can start `cultural-aspects.exe` after it is built. If the executable is missing, it falls back to the Python prototype.
- The app is still visible as a normal process to the child account. Stronger anti-bypass behavior belongs to Step 7.
- Parent password storage is still prototype-only and must be hardened later.
