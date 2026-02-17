param(
    [switch]$SkipInstall,
    [switch]$SkipIndex,
    [switch]$ForceIndex
)

$ErrorActionPreference = "Stop"

$RepoRoot = $PSScriptRoot
$DefaultCandidates = @(
    "G:\field-assist-bot",
    "D:\field-assist-bot"
)

if (-not $RepoRoot -or -not (Test-Path (Join-Path $RepoRoot ".venv\Scripts\python.exe"))) {
    $RepoRoot = $null
    foreach ($candidate in $DefaultCandidates) {
        if (Test-Path (Join-Path $candidate ".venv\Scripts\python.exe")) {
            $RepoRoot = $candidate
            break
        }
    }
}

if (-not $RepoRoot) {
    throw "Could not locate repository. Checked script location and: $($DefaultCandidates -join ', ')"
}

$VenvPython = Join-Path $RepoRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $VenvPython)) {
    throw "Python venv not found at $VenvPython. Create the venv first."
}

Push-Location $RepoRoot
try {
    if (-not $SkipInstall) {
        Write-Host "[1/3] Installing package in editable mode..." -ForegroundColor Cyan
        & $VenvPython -m pip install -e .
    }

    $CliArgs = @("-m", "src.cli")
    if ($SkipIndex) { $CliArgs += "--skip-index" }
    if ($ForceIndex) { $CliArgs += "--force-index" }

    Write-Host "[2/3] Starting bot (includes indexing unless --SkipIndex is used)..." -ForegroundColor Cyan
    & $VenvPython @CliArgs
}
finally {
    Pop-Location
}
