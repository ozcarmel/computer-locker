param(
    [string] $ProjectRoot = "C:\Cultural Aspects",
    [string] $ExeName = "cultural-aspects-activity-reporter"
)

$ErrorActionPreference = "Stop"

$resolvedProjectRoot = (Resolve-Path -LiteralPath $ProjectRoot).Path
$agentDir = Join-Path $resolvedProjectRoot "src\activity-reporting-agent"
$entryPoint = Join-Path $agentDir "activity_reporter.py"

if (-not (Test-Path -LiteralPath $entryPoint)) {
    throw "Activity reporter entry point not found at: $entryPoint"
}

Set-Location -LiteralPath $agentDir

python -m PyInstaller `
    --noconfirm `
    --clean `
    --windowed `
    --onefile `
    --name $ExeName `
    $entryPoint

$exePath = Join-Path $agentDir "dist\$ExeName.exe"
if (-not (Test-Path -LiteralPath $exePath)) {
    throw "Expected executable was not created: $exePath"
}

Write-Output "Built executable: $exePath"
