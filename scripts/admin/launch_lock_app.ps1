param(
    [string] $ProjectRoot = "C:\Cultural Aspects",
    [string] $PythonExe = ""
)

$ErrorActionPreference = "Stop"

$appDir = Join-Path $ProjectRoot "src\windows-lock-app"
$appPath = Join-Path $appDir "app.py"
$packagedExePath = Join-Path $appDir "dist\cultural-aspects.exe"

if (Test-Path -LiteralPath $packagedExePath) {
    Set-Location -LiteralPath (Split-Path -Parent $packagedExePath)
    & $packagedExePath
    exit $LASTEXITCODE
}

if (-not (Test-Path -LiteralPath $appPath)) {
    throw "Lock app not found at: $appPath"
}

if ([string]::IsNullOrWhiteSpace($PythonExe)) {
    $pythonCommand = Get-Command pythonw.exe -ErrorAction SilentlyContinue
    if ($null -eq $pythonCommand) {
        $pythonCommand = Get-Command python.exe -ErrorAction Stop
    }
    $PythonExe = $pythonCommand.Source
}

Set-Location -LiteralPath $appDir
& $PythonExe $appPath
