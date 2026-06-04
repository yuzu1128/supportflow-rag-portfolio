param(
    [int]$BackendPort = 8011,
    [int]$FrontendPort = 5179,
    [string]$Model = "gemma3:1b"
)

$ErrorActionPreference = "Stop"

$root = Resolve-Path (Join-Path $PSScriptRoot "..")
$runDir = Join-Path $root ".run"
New-Item -ItemType Directory -Force -Path $runDir | Out-Null

$ollama = Join-Path $env:LOCALAPPDATA "Programs\Ollama\ollama.exe"
if (-not (Test-Path $ollama)) {
    $ollama = "ollama"
}

try {
    Invoke-RestMethod -Uri "http://localhost:11434/api/tags" -Method Get -TimeoutSec 10 | Out-Null
} catch {
    Start-Process -FilePath $ollama -ArgumentList "serve" -WindowStyle Hidden
    Start-Sleep -Seconds 5
}

$tags = Invoke-RestMethod -Uri "http://localhost:11434/api/tags" -Method Get -TimeoutSec 20
$installed = @($tags.models | ForEach-Object { $_.name })
if ($installed -notcontains $Model) {
    & $ollama pull $Model
}

$warmupBody = @{
    model = $Model
    prompt = "Answer strictly in Japanese. One short sentence only. Warm up local model."
    stream = $false
    keep_alive = "30m"
    options = @{
        num_ctx = 512
        num_predict = 40
        temperature = 0.1
    }
} | ConvertTo-Json -Depth 6
Invoke-RestMethod -Uri "http://localhost:11434/api/generate" -Method Post -Body $warmupBody -ContentType "application/json" -TimeoutSec 180 | Out-Null

$env:DATA_DIR = Join-Path $root "data"
$env:SAMPLE_DOCS_DIR = Join-Path $root "sample_docs"
$env:LLM_PROVIDER = "ollama"
$env:OLLAMA_BASE_URL = "http://localhost:11434"
$env:OLLAMA_MODEL = $Model
$env:TOP_K = "5"
$env:VECTOR_WEIGHT = "0.6"
$env:KEYWORD_WEIGHT = "0.4"
$env:MIN_ANSWER_SCORE = "0.18"

$timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$backend = Start-Process -FilePath "python" `
    -ArgumentList @("-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "$BackendPort") `
    -WorkingDirectory (Join-Path $root "backend") `
    -WindowStyle Hidden `
    -RedirectStandardOutput (Join-Path $runDir "backend-$timestamp.out.log") `
    -RedirectStandardError (Join-Path $runDir "backend-$timestamp.err.log") `
    -PassThru

$env:VITE_API_BASE_URL = "http://localhost:$BackendPort/api"
$frontend = Start-Process -FilePath "npm.cmd" `
    -ArgumentList @("run", "dev", "--", "--host", "127.0.0.1", "--port", "$FrontendPort") `
    -WorkingDirectory (Join-Path $root "frontend") `
    -WindowStyle Hidden `
    -RedirectStandardOutput (Join-Path $runDir "frontend-$timestamp.out.log") `
    -RedirectStandardError (Join-Path $runDir "frontend-$timestamp.err.log") `
    -PassThru

@(
    "backend=$($backend.Id)"
    "frontend=$($frontend.Id)"
    "backend_url=http://localhost:$BackendPort"
    "frontend_url=http://localhost:$FrontendPort"
    "model=$Model"
) | Set-Content -LiteralPath (Join-Path $runDir "native-ollama-demo.txt") -Encoding ASCII

Write-Host "Backend:  http://localhost:$BackendPort"
Write-Host "Frontend: http://localhost:$FrontendPort"
Write-Host "Model:    $Model"
Write-Host "PID file: $runDir\native-ollama-demo.txt"
