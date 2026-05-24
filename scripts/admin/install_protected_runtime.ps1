param(
    [Parameter(Mandatory = $true)]
    [string] $ChildUsername,

    [string] $SourceProjectRoot = "C:\Cultural Aspects",
    [string] $InstallDir = "C:\Program Files\Cultural Aspects",
    [string] $RuntimeDataDir = "C:\ProgramData\Cultural Aspects",
    [string] $TaskName = "ComputerLocker-ChildLogon"
)

$ErrorActionPreference = "Stop"

function Assert-Administrator {
    $identity = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($identity)
    if (-not $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
        throw "This script must be run from an elevated Administrator PowerShell window."
    }
}

Assert-Administrator

$resolvedSourceRoot = (Resolve-Path -LiteralPath $SourceProjectRoot).Path
$sourceExe = Join-Path $resolvedSourceRoot "src\windows-lock-app\dist\cultural-aspects.exe"
$sourceLauncher = Join-Path $resolvedSourceRoot "scripts\admin\launch_lock_app.ps1"

if (-not (Test-Path -LiteralPath $sourceExe)) {
    throw "Built executable not found at: $sourceExe"
}

if (-not (Test-Path -LiteralPath $sourceLauncher)) {
    throw "Launcher script not found at: $sourceLauncher"
}

$eventsDir = Join-Path $RuntimeDataDir "data\events"
$logsDir = Join-Path $RuntimeDataDir "logs"
$installedExe = Join-Path $InstallDir "cultural-aspects.exe"
$installedLauncher = Join-Path $InstallDir "launch_lock_app.ps1"

New-Item -ItemType Directory -Force -Path $InstallDir | Out-Null
New-Item -ItemType Directory -Force -Path $eventsDir | Out-Null
New-Item -ItemType Directory -Force -Path $logsDir | Out-Null

Get-Process -Name "cultural-aspects" -ErrorAction SilentlyContinue | Stop-Process -Force

Copy-Item -LiteralPath $sourceExe -Destination $installedExe -Force
Copy-Item -LiteralPath $sourceLauncher -Destination $installedLauncher -Force

# The child account needs write access only to runtime data/logs, not to the app source.
icacls $RuntimeDataDir /grant "*S-1-5-11:(OI)(CI)M" /T | Out-Null

$actionArguments = @(
    "-NoProfile",
    "-ExecutionPolicy", "Bypass",
    "-WindowStyle", "Hidden",
    "-File", "`"$installedLauncher`"",
    "-InstalledExePath", "`"$installedExe`"",
    "-EventsDir", "`"$eventsDir`"",
    "-LogDir", "`"$logsDir`""
) -join " "

$action = New-ScheduledTaskAction `
    -Execute "powershell.exe" `
    -Argument $actionArguments `
    -WorkingDirectory $InstallDir

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
    -Description "Starts the protected Cultural Aspects runtime when the child standard user logs on."

Register-ScheduledTask `
    -TaskName $TaskName `
    -InputObject $task `
    -Force | Out-Null

Write-Output "Installed protected runtime: $installedExe"
Write-Output "Runtime data folder: $RuntimeDataDir"
Write-Output "Updated scheduled task: $TaskName"
Write-Output "Child user trigger: $ChildUsername"
Write-Output "The project source can now be hidden or ACL-protected separately."
