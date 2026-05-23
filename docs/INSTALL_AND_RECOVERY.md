# Install and Recovery

This document is the practical recovery guide for the current baseline.

## What This Baseline Contains

- Windows lock app prototype.
- Packaged executable named `cultural-aspects.exe`.
- Admin scheduled-task setup scripts.
- Local JSONL reporting data support.
- Static mobile reporting app prototype.
- End-to-end check script.

## Build

```powershell
Set-Location -LiteralPath 'C:\Cultural Aspects'
.\scripts\build\build_windows_exe.ps1
```

Expected executable:

```text
C:\Cultural Aspects\src\windows-lock-app\dist\cultural-aspects.exe
```

## Package

```powershell
Set-Location -LiteralPath 'C:\Cultural Aspects'
.\scripts\package\create_release_package.ps1
```

Expected output:

```text
C:\Cultural Aspects\release\cultural-aspects-baseline.zip
```

The package includes the executable, mobile reporting app, admin scripts, and documentation. It does not include runtime logs, child usage data, local secrets, or build cache folders.

## Run Automated Checks

```powershell
Set-Location -LiteralPath 'C:\Cultural Aspects'
.\scripts\test\run_e2e_checks.ps1 -SkipBuild
```

Use the full version when you want to rebuild first:

```powershell
.\scripts\test\run_e2e_checks.ps1
```

## Install Startup Task

This requires an elevated Administrator PowerShell window:

```powershell
Set-Location -LiteralPath 'C:\Cultural Aspects'
.\scripts\admin\install_startup_task.ps1 -ChildUsername 'FBI\gilic'
```

The task name is:

```text
ComputerLocker-ChildLogon
```

## Remove Startup Task

This requires an elevated Administrator PowerShell window:

```powershell
Set-Location -LiteralPath 'C:\Cultural Aspects'
.\scripts\admin\uninstall_startup_task.ps1
```

## Export Mobile Report Data

```powershell
Set-Location -LiteralPath 'C:\Cultural Aspects\src\windows-lock-app'
python .\generate_report.py --output ..\mobile-reporting-app\report-data.json
```

## Serve Mobile Report Locally

```powershell
Set-Location -LiteralPath 'C:\Cultural Aspects\src\mobile-reporting-app'
python -m http.server 8088
```

Open:

```text
http://127.0.0.1:8088
```

## Restore Project Baseline

If something goes wrong:

1. Return to `C:\Cultural Aspects`.
2. Read `PROJECT_REFERENCE.md`.
3. Read `AGENTS.md`.
4. Run `.\scripts\test\run_e2e_checks.ps1 -SkipBuild`.
5. If files were changed badly, restore from Git after the stable baseline commit.
6. Rebuild `cultural-aspects.exe` with `.\scripts\build\build_windows_exe.ps1`.

## Data and Secrets

Do not commit:

- `data\events`
- `logs`
- `config\*.local.json`
- password or secret files
- `report-data.json`

These are ignored by `.gitignore`.
