# Smoke: POST analytics events through api-gateway -> session-service.
$ErrorActionPreference = "Stop"

$scriptsDir = $PSScriptRoot
$root = Split-Path $scriptsDir -Parent
$analyticsFilePath = Join-Path $root "services\session-service\data\analytics_events.json"
$goRoot = "C:\toolchains\go1.24.3-tar\go"
$api = "http://localhost:8080"
$deviceId = "smoke_device_analytics"

function Stop-PortProcess {
  param([int[]]$Ports)
  $connections = Get-NetTCPConnection -LocalPort $Ports -State Listen -ErrorAction SilentlyContinue
  if (-not $connections) { return }
  $connections | Select-Object -ExpandProperty OwningProcess | Sort-Object -Unique |
    ForEach-Object { Stop-Process -Id $_ -Force -ErrorAction SilentlyContinue }
}

function Wait-HttpOk {
  param([string]$Url, [int]$TimeoutSeconds = 40)
  $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
  while ((Get-Date) -lt $deadline) {
    try {
      $r = Invoke-WebRequest -Uri $Url -UseBasicParsing -TimeoutSec 2
      if ($r.StatusCode -eq 200) { return }
    } catch { Start-Sleep -Milliseconds 500 }
  }
  throw "Timeout waiting for $Url"
}

function Start-GoService {
  param([string]$ScriptName, [hashtable]$ExtraEnv = @{})
  $envBlock = @("set ""GOROOT=$goRoot""", "set ""PATH=$($goRoot)\bin;%PATH%""")
  foreach ($pair in $ExtraEnv.GetEnumerator()) {
    $envBlock += "set ""$($pair.Key)=$($pair.Value)"""
  }
  $fullCommand = ($envBlock + @("call .\$ScriptName")) -join " && "
  return Start-Process -FilePath "cmd.exe" -ArgumentList "/c", $fullCommand -WorkingDirectory $scriptsDir -WindowStyle Hidden -PassThru
}

Stop-PortProcess -Ports @(8080, 8082)
if (Test-Path $analyticsFilePath) { Remove-Item $analyticsFilePath -Force }

$sessionProc = $null
$gatewayProc = $null

try {
  $sessionProc = Start-GoService -ScriptName "run-session-service.cmd" -ExtraEnv @{
    SESSION_REPOSITORY_BACKEND   = "file"
    ANALYTICS_EVENTS_FILE_PATH   = $analyticsFilePath
  }
  $gatewayProc = Start-GoService -ScriptName "run-api-gateway.cmd"

  Wait-HttpOk "$api/healthz"
  Wait-HttpOk "http://localhost:8082/healthz"

  $body = @{
    events = @(
      @{
        event      = "onboarding_complete"
        properties = @{ goal = "job_interview"; roleId = "product" }
        at         = (Get-Date).ToUniversalTime().ToString("o")
      },
      @{
        event      = "quest_start"
        properties = @{ questPackId = "interview"; missionId = "self_intro" }
        at         = (Get-Date).ToUniversalTime().ToString("o")
      }
    )
  } | ConvertTo-Json -Depth 6 -Compress

  $result = Invoke-RestMethod -Method Post -Uri "$api/v1/mobile/analytics/events" `
    -ContentType "application/json" `
    -Headers @{ "X-Device-Id" = $deviceId } `
    -Body $body

  if ($result.accepted -ne 2) {
    throw "Expected accepted=2, got $($result.accepted)"
  }

  if (-not (Test-Path $analyticsFilePath)) {
    throw "Expected analytics file at $analyticsFilePath"
  }

  $stored = Get-Content $analyticsFilePath -Raw | ConvertFrom-Json
  if ($stored.Count -lt 2) {
    throw "Expected at least 2 stored analytics events"
  }

  Write-Host "smoke-analytics-events: OK"
  Write-Host "  accepted=$($result.accepted)"
  Write-Host "  file=$analyticsFilePath"
}
finally {
  Stop-PortProcess -Ports @(8080, 8082)
  if ($sessionProc) { Stop-Process -Id $sessionProc.Id -Force -ErrorAction SilentlyContinue }
  if ($gatewayProc) { Stop-Process -Id $gatewayProc.Id -Force -ErrorAction SilentlyContinue }
}
