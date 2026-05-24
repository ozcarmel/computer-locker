param(
    [Parameter(Mandatory = $true)]
    [string] $ChildUsername,

    [string] $ProjectRoot = "C:\Cultural Aspects",
    [string] $InstallDir = "C:\Program Files\Cultural Aspects",
    [string] $RuntimeDataDir = "C:\ProgramData\Cultural Aspects",
    [string] $PythonExe = "",
    [string] $MonitorTaskName = "CulturalAspects-ActivityMonitor",
    [string] $ReportTaskName = "CulturalAspects-ActivityReport"
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
$agentDir = Join-Path $resolvedProjectRoot "src\activity-reporting-agent"
$agentPath = Join-Path $agentDir "activity_reporter.py"
$sourceAgentExe = Join-Path $agentDir "dist\cultural-aspects-activity-reporter.exe"
$installedAgentExe = Join-Path $InstallDir "cultural-aspects-activity-reporter.exe"
$resolvedPythonExe = Resolve-Python $PythonExe

if (-not (Test-Path -LiteralPath $agentPath) -and -not (Test-Path -LiteralPath $sourceAgentExe)) {
    throw "Activity reporter not found at: $agentPath"
}

$activityDir = Join-Path $RuntimeDataDir "activity"
$lockEventsDir = Join-Path $RuntimeDataDir "data\events"
$reportPath = Join-Path $RuntimeDataDir "activity-report.json"
$mobileReportPath = Join-Path $resolvedProjectRoot "src\mobile-reporting-app\activity-report.json"

New-Item -ItemType Directory -Force -Path $activityDir | Out-Null
New-Item -ItemType Directory -Force -Path $InstallDir | Out-Null
New-Item -ItemType Directory -Force -Path (Split-Path -Parent $reportPath) | Out-Null
New-Item -ItemType Directory -Force -Path (Split-Path -Parent $mobileReportPath) | Out-Null

# The child account writes runtime samples and the generated local report.
icacls $RuntimeDataDir /grant "*S-1-5-11:(OI)(CI)M" /T | Out-Null

if (Test-Path -LiteralPath $sourceAgentExe) {
    Get-Process -Name "cultural-aspects-activity-reporter" -ErrorAction SilentlyContinue | Stop-Process -Force
    Copy-Item -LiteralPath $sourceAgentExe -Destination $installedAgentExe -Force
    $agentExecute = $installedAgentExe
    $monitorArguments = @(
        "--mode", "monitor",
        "--activity-dir", "`"$activityDir`"",
        "--interval-seconds", "30"
    ) -join " "
    $reportArguments = @(
        "--mode", "report",
        "--activity-dir", "`"$activityDir`"",
        "--lock-events-dir", "`"$lockEventsDir`"",
        "--output", "`"$reportPath`"",
        "--mobile-output", "`"$mobileReportPath`"",
        "--hours", "12"
    ) -join " "
}
else {
    $agentExecute = $resolvedPythonExe
    $monitorArguments = @(
        "`"$agentPath`"",
        "--mode", "monitor",
        "--activity-dir", "`"$activityDir`"",
        "--interval-seconds", "30"
    ) -join " "
    $reportArguments = @(
        "`"$agentPath`"",
        "--mode", "report",
        "--activity-dir", "`"$activityDir`"",
        "--lock-events-dir", "`"$lockEventsDir`"",
        "--output", "`"$reportPath`"",
        "--mobile-output", "`"$mobileReportPath`"",
        "--hours", "12"
    ) -join " "
}

$monitorAction = New-ScheduledTaskAction `
    -Execute $agentExecute `
    -Argument $monitorArguments `
    -WorkingDirectory $InstallDir

$monitorTrigger = New-ScheduledTaskTrigger -AtLogOn -User $ChildUsername
$monitorTrigger.Delay = "PT45S"

$principal = New-ScheduledTaskPrincipal `
    -UserId $ChildUsername `
    -LogonType Interactive `
    -RunLevel Limited

$monitorSettings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -ExecutionTimeLimit (New-TimeSpan -Days 1) `
    -MultipleInstances IgnoreNew `
    -RestartCount 3 `
    -RestartInterval (New-TimeSpan -Minutes 1) `
    -StartWhenAvailable

$monitorTask = New-ScheduledTask `
    -Action $monitorAction `
    -Trigger $monitorTrigger `
    -Principal $principal `
    -Settings $monitorSettings `
    -Description "Samples Gili's active app/window for parent activity reporting."

Register-ScheduledTask `
    -TaskName $MonitorTaskName `
    -InputObject $monitorTask `
    -Force | Out-Null

$reportAction = New-ScheduledTaskAction `
    -Execute $agentExecute `
    -Argument $reportArguments `
    -WorkingDirectory $InstallDir

$morningTrigger = New-ScheduledTaskTrigger -Daily -At 8:00AM
$eveningTrigger = New-ScheduledTaskTrigger -Daily -At 8:00PM

$reportSettings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -ExecutionTimeLimit (New-TimeSpan -Minutes 10) `
    -MultipleInstances IgnoreNew `
    -StartWhenAvailable

$reportTask = New-ScheduledTask `
    -Action $reportAction `
    -Trigger @($morningTrigger, $eveningTrigger) `
    -Principal $principal `
    -Settings $reportSettings `
    -Description "Generates the parent activity report twice per day."

Register-ScheduledTask `
    -TaskName $ReportTaskName `
    -InputObject $reportTask `
    -Force | Out-Null

Write-Output "Installed activity monitor task: $MonitorTaskName"
Write-Output "Installed activity report task: $ReportTaskName"
Write-Output "Activity reporter executable: $agentExecute"
Write-Output "Child user: $ChildUsername"
Write-Output "Activity data folder: $activityDir"
Write-Output "Activity report: $reportPath"
Write-Output "Mobile app report target: $mobileReportPath"
