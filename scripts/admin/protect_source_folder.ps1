param(
    [string] $SourceProjectRoot = "C:\Cultural Aspects",
    [string] $AdminUsername = "FBI\ozcar",
    [string] $ChildUsername = "FBI\gilic"
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

if ($resolvedSourceRoot -ieq "C:\" -or $resolvedSourceRoot.Length -lt 8) {
    throw "Refusing to protect suspicious source path: $resolvedSourceRoot"
}

attrib +h +s $resolvedSourceRoot

icacls $resolvedSourceRoot /inheritance:r | Out-Null
icacls $resolvedSourceRoot /grant:r "SYSTEM:(OI)(CI)F" | Out-Null
icacls $resolvedSourceRoot /grant:r "BUILTIN\Administrators:(OI)(CI)F" | Out-Null
icacls $resolvedSourceRoot /grant:r "${AdminUsername}:(OI)(CI)F" | Out-Null
icacls $resolvedSourceRoot /remove:g "BUILTIN\Users" "NT AUTHORITY\Authenticated Users" $ChildUsername 2>$null | Out-Null

Write-Output "Protected source folder: $resolvedSourceRoot"
Write-Output "Allowed: SYSTEM, BUILTIN\Administrators, $AdminUsername"
Write-Output "Removed access for standard users and $ChildUsername where present."
Write-Output "Important: run future development from the admin account or clone the GitHub repo elsewhere."
