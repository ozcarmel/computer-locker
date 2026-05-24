param(
    [string] $ProjectRoot = "C:\Cultural Aspects",
    [string] $PythonExe = "",
    [string] $InstalledExePath = "",
    [string] $EventsDir = "",
    [string] $LogDir = ""
)

$ErrorActionPreference = "Stop"

if ([string]::IsNullOrWhiteSpace($LogDir)) {
    $LogDir = Join-Path $ProjectRoot "logs"
}

$logPath = Join-Path $LogDir "launcher.log"

function Write-LauncherLog {
    param([string] $Message)

    New-Item -ItemType Directory -Force -Path $LogDir | Out-Null
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $identity = [Security.Principal.WindowsIdentity]::GetCurrent().Name
    Add-Content -LiteralPath $logPath -Value "[$timestamp] [$identity] $Message"
}

Write-LauncherLog "Launcher started. ProjectRoot=$ProjectRoot PythonExe=$PythonExe InstalledExePath=$InstalledExePath"

$appDir = Join-Path $ProjectRoot "src\windows-lock-app"
$appPath = Join-Path $appDir "app.py"
$packagedExePath = Join-Path $appDir "dist\cultural-aspects.exe"

if ([string]::IsNullOrWhiteSpace($EventsDir)) {
    $EventsDir = Join-Path $ProjectRoot "data\events"
}

$env:LOCK_APP_EVENTS_DIR = $EventsDir

try {
    if (-not [string]::IsNullOrWhiteSpace($InstalledExePath)) {
        if (-not (Test-Path -LiteralPath $InstalledExePath)) {
            throw "Installed executable not found at: $InstalledExePath"
        }

        Write-LauncherLog "Starting installed executable: $InstalledExePath"
        Set-Location -LiteralPath (Split-Path -Parent $InstalledExePath)
        $process = Start-Process -FilePath $InstalledExePath -WorkingDirectory (Split-Path -Parent $InstalledExePath) -PassThru -Wait
        Write-LauncherLog "Installed executable exited. ExitCode=$($process.ExitCode)"
        exit $process.ExitCode
    }

    if (Test-Path -LiteralPath $packagedExePath) {
        Write-LauncherLog "Starting packaged executable: $packagedExePath"
        Set-Location -LiteralPath $appDir
        $process = Start-Process -FilePath $packagedExePath -WorkingDirectory $appDir -PassThru -Wait
        Write-LauncherLog "Packaged executable exited. ExitCode=$($process.ExitCode)"
        exit $process.ExitCode
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

    Write-LauncherLog "Starting Python app: $PythonExe $appPath"
    Set-Location -LiteralPath $appDir
    & $PythonExe $appPath
    Write-LauncherLog "Python app exited. ExitCode=$LASTEXITCODE"
    exit $LASTEXITCODE
}
catch {
    Write-LauncherLog "Launcher failed: $($_.Exception.Message)"
    throw
}
