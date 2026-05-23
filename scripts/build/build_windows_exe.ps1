param(
    [string] $ProjectRoot = "C:\Cultural Aspects",
    [string] $ExeName = "cultural-aspects"
)

$ErrorActionPreference = "Stop"

$resolvedProjectRoot = (Resolve-Path -LiteralPath $ProjectRoot).Path
$appDir = Join-Path $resolvedProjectRoot "src\windows-lock-app"
$entryPoint = Join-Path $appDir "app.py"

if (-not (Test-Path -LiteralPath $entryPoint)) {
    throw "App entry point not found at: $entryPoint"
}

Set-Location -LiteralPath $appDir

python -m PyInstaller `
    --noconfirm `
    --clean `
    --windowed `
    --onefile `
    --name $ExeName `
    $entryPoint

$exePath = Join-Path $appDir "dist\$ExeName.exe"
if (-not (Test-Path -LiteralPath $exePath)) {
    throw "Expected executable was not created: $exePath"
}

Write-Output "Built executable: $exePath"
