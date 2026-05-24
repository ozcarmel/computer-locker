param(
    [Parameter(Mandatory = $true)]
    [string] $ChildUsername,

    [string] $ProjectRoot = "C:\Cultural Aspects",
    [string] $TaskName = "ComputerLocker-ChildLogon",
    [string] $PythonExe = ""
)

$ErrorActionPreference = "Stop"

function Assert-Administrator {
    $identity = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($identity)
    if (-not $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
        throw "This script must be run from an elevated Administrator PowerShell window."
    }
}

function Resolve-Python {
    param([string] $RequestedPythonExe)

    if (-not [string]::IsNullOrWhiteSpace($RequestedPythonExe)) {
        if (-not (Test-Path -LiteralPath $RequestedPythonExe)) {
            throw "Python executable not found at: $RequestedPythonExe"
        }
        return (Resolve-Path -LiteralPath $RequestedPythonExe).Path
    }

    $pythonCommand = Get-Command pythonw.exe -ErrorAction SilentlyContinue
    if ($null -eq $pythonCommand) {
        $pythonCommand = Get-Command python.exe -ErrorAction Stop
    }
    return $pythonCommand.Source
}

Assert-Administrator

$resolvedProjectRoot = (Resolve-Path -LiteralPath $ProjectRoot).Path
$launcherPath = Join-Path $resolvedProjectRoot "scripts\admin\launch_lock_app.ps1"
$appPath = Join-Path $resolvedProjectRoot "src\windows-lock-app\app.py"
$resolvedPythonExe = Resolve-Python $PythonExe

if (-not (Test-Path -LiteralPath $launcherPath)) {
    throw "Launcher script not found at: $launcherPath"
}

if (-not (Test-Path -LiteralPath $appPath)) {
    throw "Lock app not found at: $appPath"
}

$actionArguments = @(
    "-NoProfile",
    "-ExecutionPolicy", "Bypass",
    "-WindowStyle", "Hidden",
    "-File", "`"$launcherPath`"",
    "-ProjectRoot", "`"$resolvedProjectRoot`"",
    "-PythonExe", "`"$resolvedPythonExe`""
) -join " "

$action = New-ScheduledTaskAction `
    -Execute "powershell.exe" `
    -Argument $actionArguments `
    -WorkingDirectory $resolvedProjectRoot

$trigger = New-ScheduledTaskTrigger -AtLogOn -User $ChildUsername
$trigger.Delay = "PT30S"
$principal = New-ScheduledTaskPrincipal `
    -UserId $ChildUsername `
    -LogonType Interactive `
    -RunLevel Limited

$settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -ExecutionTimeLimit (New-TimeSpan -Hours 12) `
    -MultipleInstances IgnoreNew `
    -RestartCount 3 `
    -RestartInterval (New-TimeSpan -Minutes 1) `
    -StartWhenAvailable

$task = New-ScheduledTask `
    -Action $action `
    -Trigger $trigger `
    -Principal $principal `
    -Settings $settings `
    -Description "Starts the Computer Locker app when the child standard user logs on."

Register-ScheduledTask `
    -TaskName $TaskName `
    -InputObject $task `
    -Force | Out-Null

Write-Output "Installed scheduled task: $TaskName"
Write-Output "Child user trigger: $ChildUsername"
Write-Output "Project root: $resolvedProjectRoot"
Write-Output "Python executable: $resolvedPythonExe"
Write-Output "The task is created by Administrator but runs in the child user's interactive logon session so the lock screen can be visible."
