param(
    [string] $ProjectRoot = "C:\Cultural Aspects",
    [switch] $SkipBuild
)

$ErrorActionPreference = "Stop"

function Write-Step {
    param([string] $Message)
    Write-Output ""
    Write-Output "== $Message =="
}

$resolvedProjectRoot = (Resolve-Path -LiteralPath $ProjectRoot).Path
$windowsAppDir = Join-Path $resolvedProjectRoot "src\windows-lock-app"
$mobileAppDir = Join-Path $resolvedProjectRoot "src\mobile-reporting-app"
$exePath = Join-Path $windowsAppDir "dist\cultural-aspects.exe"
$reportPath = Join-Path $mobileAppDir "report-data.json"

Write-Step "Python unit tests"
Push-Location -LiteralPath $windowsAppDir
python -m unittest discover -s tests
Pop-Location

Write-Step "PowerShell script syntax"
$scripts = @(
    "scripts\admin\install_startup_task.ps1",
    "scripts\admin\install_protected_runtime.ps1",
    "scripts\admin\launch_lock_app.ps1",
    "scripts\admin\protect_source_folder.ps1",
    "scripts\admin\uninstall_startup_task.ps1",
    "scripts\build\build_windows_exe.ps1",
    "scripts\package\create_release_package.ps1",
    "scripts\test\run_e2e_checks.ps1"
)

foreach ($relativeScript in $scripts) {
    $scriptPath = Join-Path $resolvedProjectRoot $relativeScript
    $tokens = $null
    $errors = $null
    [System.Management.Automation.Language.Parser]::ParseFile($scriptPath, [ref] $tokens, [ref] $errors) | Out-Null
    if ($errors.Count -gt 0) {
        $errors | ForEach-Object { Write-Error "${relativeScript}: $($_.Message)" }
        exit 1
    }
}
Write-Output "PowerShell syntax check passed"

if (-not $SkipBuild) {
    Write-Step "Build cultural-aspects.exe"
    & (Join-Path $resolvedProjectRoot "scripts\build\build_windows_exe.ps1") -ProjectRoot $resolvedProjectRoot
}

Write-Step "Verify executable"
if (-not (Test-Path -LiteralPath $exePath)) {
    throw "Missing executable: $exePath"
}
Get-Item -LiteralPath $exePath | Select-Object Name, Length, FullName

Write-Step "Export report JSON"
Push-Location -LiteralPath $windowsAppDir
python .\generate_report.py --output $reportPath
Pop-Location

if (-not (Test-Path -LiteralPath $reportPath)) {
    throw "Missing generated report: $reportPath"
}
Get-Content -Raw -Path $reportPath | ConvertFrom-Json | Out-Null
Write-Output "Report JSON is valid"

Write-Step "Verify mobile app files"
$requiredMobileFiles = @(
    "index.html",
    "styles.css",
    "app.js",
    "manifest.webmanifest",
    "service-worker.js"
)
foreach ($file in $requiredMobileFiles) {
    $path = Join-Path $mobileAppDir $file
    if (-not (Test-Path -LiteralPath $path)) {
        throw "Missing mobile app file: $path"
    }
}
Write-Output "Mobile app files are present"

Write-Step "Scheduled task cmdlet compatibility"
$checks = @(
    ((Get-Command New-ScheduledTaskTrigger).Parameters.Keys -contains "User"),
    ((Get-Command New-ScheduledTaskPrincipal).Parameters.Keys -contains "LogonType"),
    ((Get-Command New-ScheduledTaskSettingsSet).Parameters.Keys -contains "RestartCount"),
    ((Get-Command Register-ScheduledTask).Parameters.Keys -contains "InputObject")
)
if ($checks -contains $false) {
    throw "This Windows install is missing a scheduled-task parameter required by the setup scripts."
}
Write-Output "Scheduled-task cmdlets are compatible"

Write-Step "E2E checks complete"
Write-Output "Automated end-to-end checks passed."
