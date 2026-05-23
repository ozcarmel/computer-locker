param(
    [string] $ProjectRoot = "C:\Cultural Aspects",
    [string] $PackageName = "cultural-aspects-baseline"
)

$ErrorActionPreference = "Stop"

$resolvedProjectRoot = (Resolve-Path -LiteralPath $ProjectRoot).Path
$windowsAppDir = Join-Path $resolvedProjectRoot "src\windows-lock-app"
$mobileAppDir = Join-Path $resolvedProjectRoot "src\mobile-reporting-app"
$exePath = Join-Path $windowsAppDir "dist\cultural-aspects.exe"
$releaseRoot = Join-Path $resolvedProjectRoot "release"
$packageDir = Join-Path $releaseRoot $PackageName
$zipPath = Join-Path $releaseRoot "$PackageName.zip"

if (-not (Test-Path -LiteralPath $exePath)) {
    & (Join-Path $resolvedProjectRoot "scripts\build\build_windows_exe.ps1") -ProjectRoot $resolvedProjectRoot
}

if (Test-Path -LiteralPath $packageDir) {
    Remove-Item -LiteralPath $packageDir -Recurse -Force
}

New-Item -ItemType Directory -Force -Path $packageDir | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $packageDir "app") | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $packageDir "mobile-reporting-app") | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $packageDir "scripts") | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $packageDir "docs") | Out-Null

Copy-Item -LiteralPath $exePath -Destination (Join-Path $packageDir "app\cultural-aspects.exe") -Force
Copy-Item -LiteralPath (Join-Path $mobileAppDir "index.html") -Destination (Join-Path $packageDir "mobile-reporting-app") -Force
Copy-Item -LiteralPath (Join-Path $mobileAppDir "styles.css") -Destination (Join-Path $packageDir "mobile-reporting-app") -Force
Copy-Item -LiteralPath (Join-Path $mobileAppDir "app.js") -Destination (Join-Path $packageDir "mobile-reporting-app") -Force
Copy-Item -LiteralPath (Join-Path $mobileAppDir "manifest.webmanifest") -Destination (Join-Path $packageDir "mobile-reporting-app") -Force
Copy-Item -LiteralPath (Join-Path $mobileAppDir "service-worker.js") -Destination (Join-Path $packageDir "mobile-reporting-app") -Force
Copy-Item -LiteralPath (Join-Path $mobileAppDir "report-data.sample.json") -Destination (Join-Path $packageDir "mobile-reporting-app") -Force
Copy-Item -LiteralPath (Join-Path $resolvedProjectRoot "scripts\admin") -Destination (Join-Path $packageDir "scripts") -Recurse -Force
Copy-Item -LiteralPath (Join-Path $resolvedProjectRoot "scripts\build") -Destination (Join-Path $packageDir "scripts") -Recurse -Force
Copy-Item -LiteralPath (Join-Path $resolvedProjectRoot "scripts\test") -Destination (Join-Path $packageDir "scripts") -Recurse -Force
Copy-Item -LiteralPath (Join-Path $resolvedProjectRoot "docs") -Destination $packageDir -Recurse -Force
Copy-Item -LiteralPath (Join-Path $resolvedProjectRoot "README.md") -Destination $packageDir -Force
Copy-Item -LiteralPath (Join-Path $resolvedProjectRoot "PROJECT_REFERENCE.md") -Destination $packageDir -Force
Copy-Item -LiteralPath (Join-Path $resolvedProjectRoot "AGENTS.md") -Destination $packageDir -Force

if (Test-Path -LiteralPath $zipPath) {
    Remove-Item -LiteralPath $zipPath -Force
}

Compress-Archive -Path (Join-Path $packageDir "*") -DestinationPath $zipPath -Force

if (-not (Test-Path -LiteralPath $zipPath)) {
    throw "Expected release zip was not created: $zipPath"
}

Write-Output "Created release folder: $packageDir"
Write-Output "Created release zip: $zipPath"
