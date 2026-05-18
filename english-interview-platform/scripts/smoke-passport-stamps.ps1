# Passport stamps API: bootstrap -> turn -> POST stamp -> GET list
$ErrorActionPreference = "Stop"

$scriptsDir = $PSScriptRoot
$root = Split-Path $scriptsDir -Parent
$sessionFilePath = Join-Path $root "services\session-service\data\sessions.json"
$stampFilePath = Join-Path $root "services\session-service\data\passport_stamps.json"
$goRoot = "C:\toolchains\go1.24.3-tar\go"
$api = "http://localhost:8080"
$deviceId = "smoke_device_001"

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
if (Test-Path $sessionFilePath) { Remove-Item $sessionFilePath -Force }
if (Test-Path $stampFilePath) { Remove-Item $stampFilePath -Force }

$sessionProc = $null
$gatewayProc = $null

try {
  $sessionProc = Start-GoService -ScriptName "run-session-service.cmd" -ExtraEnv @{
    SESSION_REPOSITORY_BACKEND = "file"
    SESSION_FILE_PATH          = $sessionFilePath
    PASSPORT_STAMPS_FILE_PATH  = $stampFilePath
  }
  $gatewayProc = Start-GoService -ScriptName "run-api-gateway.cmd"

  Wait-HttpOk "$api/healthz"
  Wait-HttpOk "http://localhost:8082/healthz"

  $headers = @{ "X-Device-Id" = $deviceId }

  $bootstrap = Invoke-RestMethod -Method Post -Uri "$api/v1/mobile/session/bootstrap" `
    -ContentType "application/json" `
    -Headers $headers `
    -Body (@{ roleId = "product"; missionId = "self_intro" } | ConvertTo-Json -Compress)

  $answer = "I led a product launch that improved activation by twenty percent in one quarter."
  $null = Invoke-RestMethod -Method Post -Uri "$api/v1/mobile/sessions/$($bootstrap.sessionId)/turns" `
    -ContentType "application/json" `
    -Headers $headers `
    -Body (@{ answer = $answer } | ConvertTo-Json -Compress)

  $issued = Invoke-RestMethod -Method Post -Uri "$api/v1/mobile/passport/stamps" `
    -ContentType "application/json" `
    -Headers $headers `
    -Body (@{
      sessionId    = $bootstrap.sessionId
      missionLabel = "Self Introduction"
      roleLabel    = "Product Manager"
    } | ConvertTo-Json -Compress)

  if (-not $issued.isNew) {
    throw "Expected isNew=true on first stamp issue"
  }

  $listed = Invoke-RestMethod -Method Get -Uri "$api/v1/mobile/passport/stamps" -Headers $headers
  if (-not $listed.stamps -or $listed.stamps.Count -lt 1) {
    throw "Expected at least one stamp in list"
  }

  Write-Host "smoke-passport-stamps: OK stampId=$($issued.id) readiness=$($issued.readiness)"
}
finally {
  if ($sessionProc -and -not $sessionProc.HasExited) {
    Stop-Process -Id $sessionProc.Id -Force -ErrorAction SilentlyContinue
  }
  if ($gatewayProc -and -not $gatewayProc.HasExited) {
    Stop-Process -Id $gatewayProc.Id -Force -ErrorAction SilentlyContinue
  }
}
