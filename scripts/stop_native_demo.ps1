$ErrorActionPreference = "SilentlyContinue"

$root = Resolve-Path (Join-Path $PSScriptRoot "..")
$pidFile = Join-Path $root ".run\native-ollama-demo.txt"

if (-not (Test-Path $pidFile)) {
    Write-Host "No native demo PID file found."
    exit 0
}

$ports = @()

Get-Content $pidFile | ForEach-Object {
    if ($_ -match "^(backend|frontend)=(\d+)$") {
        Stop-Process -Id ([int]$Matches[2]) -Force
    }
    if ($_ -match "^.+_url=http://localhost:(\d+)$") {
        $ports += [int]$Matches[1]
    }
}

$ports | Select-Object -Unique | ForEach-Object {
    Get-NetTCPConnection -LocalPort $_ -State Listen | ForEach-Object {
        Stop-Process -Id $_.OwningProcess -Force
    }
}

Write-Host "Stopped native demo processes listed in $pidFile"
