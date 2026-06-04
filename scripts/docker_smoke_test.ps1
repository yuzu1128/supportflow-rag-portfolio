param(
    [switch]$SkipBuild,
    [switch]$Down
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$repoRoot = Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..")
Set-Location -LiteralPath $repoRoot

$dockerBinDir = "C:\Program Files\Docker\Docker\resources\bin"
if (Test-Path -LiteralPath $dockerBinDir) {
    $env:PATH = "$dockerBinDir;C:\Program Files\Docker\Docker\resources;$env:PATH"
}

$docker = "docker"
if (Test-Path -LiteralPath (Join-Path $dockerBinDir "docker.exe")) {
    $docker = Join-Path $dockerBinDir "docker.exe"
}

function Read-DotEnvValue {
    param(
        [string]$Name,
        [string]$Default
    )

    $envPath = Join-Path $repoRoot ".env"
    if (-not (Test-Path -LiteralPath $envPath)) {
        return $Default
    }

    $pattern = "^\s*$([regex]::Escape($Name))\s*=\s*(.*)\s*$"
    foreach ($line in Get-Content -LiteralPath $envPath) {
        if ($line -match $pattern) {
            $value = $Matches[1].Trim()
            if ($value.StartsWith('"') -and $value.EndsWith('"')) {
                $value = $value.Substring(1, $value.Length - 2)
            }
            if ($value.StartsWith("'") -and $value.EndsWith("'")) {
                $value = $value.Substring(1, $value.Length - 2)
            }
            if ($value.Length -gt 0) {
                return $value
            }
        }
    }
    return $Default
}

function Wait-BackendHealth {
    param([string]$HealthUrl)

    for ($i = 1; $i -le 60; $i++) {
        try {
            $response = Invoke-RestMethod -Uri $HealthUrl -TimeoutSec 5
            if ($response.status -eq "ok") {
                return
            }
        }
        catch {
            Start-Sleep -Seconds 2
        }
    }
    throw "Backend did not become healthy at $HealthUrl"
}

if (-not (Test-Path -LiteralPath (Join-Path $repoRoot ".env"))) {
    Copy-Item -LiteralPath (Join-Path $repoRoot ".env.example") -Destination (Join-Path $repoRoot ".env")
}

& $docker compose config --quiet

if ($SkipBuild) {
    & $docker compose up -d
}
else {
    & $docker compose up -d --build
}

$backendPort = Read-DotEnvValue -Name "BACKEND_PORT" -Default "8000"
$frontendPort = Read-DotEnvValue -Name "FRONTEND_PORT" -Default "5173"
$apiBase = Read-DotEnvValue -Name "VITE_API_BASE_URL" -Default "http://localhost:$backendPort/api"
$backendBase = $apiBase -replace "/api/?$", ""
$frontendBase = "http://localhost:$frontendPort"

Wait-BackendHealth -HealthUrl "$backendBase/health"

$frontendResponse = Invoke-WebRequest -Uri $frontendBase -UseBasicParsing -TimeoutSec 15
if ($frontendResponse.StatusCode -ne 200) {
    throw "Frontend returned HTTP $($frontendResponse.StatusCode)"
}

$dashboard = Invoke-RestMethod -Uri "$apiBase/dashboard" -TimeoutSec 30
if (-not $dashboard.documents -or $dashboard.documents.Count -lt 30) {
    throw "Dashboard document count is unexpectedly low."
}

$askBody = @{
    question = "How should AUTH_401 token expired errors be handled?"
    k = 5
} | ConvertTo-Json
$ask = Invoke-RestMethod -Uri "$apiBase/ask" -Method Post -Body $askBody -ContentType "application/json" -TimeoutSec 30
if (-not $ask.citations -or $ask.citations.Count -lt 1) {
    throw "Ask endpoint returned no citations."
}

$evalBody = @{
    name = "docker-smoke"
    k = 5
} | ConvertTo-Json
$eval = Invoke-RestMethod -Uri "$apiBase/evaluation/run" -Method Post -Body $evalBody -ContentType "application/json" -TimeoutSec 120
if (-not $eval.available -or $eval.case_count -lt 30) {
    throw "Evaluation run did not complete as expected."
}

$summary = [PSCustomObject]@{
    frontend = $frontendBase
    backend = $backendBase
    documents = $dashboard.documents.Count
    provider = $ask.provider
    citations = $ask.citations.Count
    case_count = $eval.case_count
    recall_at_3 = [Math]::Round([double]$eval.metrics.recall_at_3, 3)
    recall_at_5 = [Math]::Round([double]$eval.metrics.recall_at_5, 3)
    mrr = [Math]::Round([double]$eval.metrics.mrr, 3)
    citation_rate = [Math]::Round([double]$eval.metrics.citation_rate, 3)
    abstention_accuracy = [Math]::Round([double]$eval.metrics.abstention_accuracy, 3)
    expected_keyword_match_rate = [Math]::Round([double]$eval.metrics.expected_keyword_match_rate, 3)
}

$summary | ConvertTo-Json

if ($Down) {
    & $docker compose down
}
