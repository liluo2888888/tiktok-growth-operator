# R1 API smoke: bootstrap -> turn -> feedback-shaped session detail (scores + turns).
$ErrorActionPreference = "Stop"

$scriptsDir = $PSScriptRoot
$root = Split-Path $scriptsDir -Parent
$sessionFilePath = Join-Path $root "services\session-service\data\sessions.json"
$goRoot = "C:\toolchains\go1.24.3-tar\go"
$api = "http://localhost:8080"

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

$sessionProc = $null
$gatewayProc = $null

try {
  $sessionProc = Start-GoService -ScriptName "run-session-service.cmd" -ExtraEnv @{
    SESSION_REPOSITORY_BACKEND = "file"
    SESSION_FILE_PATH          = $sessionFilePath
  }
  $gatewayProc = Start-GoService -ScriptName "run-api-gateway.cmd"

  Wait-HttpOk "$api/healthz"
  Wait-HttpOk "http://localhost:8082/healthz"

  $bootstrap = Invoke-RestMethod -Method Post -Uri "$api/v1/mobile/session/bootstrap" `
    -ContentType "application/json" `
    -Body (@{ roleId = "product"; missionId = "self_intro" } | ConvertTo-Json -Compress)

  $answer = "I am a product manager with five years experience leading cross functional teams to ship user facing features on schedule."
  $turn = Invoke-RestMethod -Method Post -Uri "$api/v1/mobile/sessions/$($bootstrap.sessionId)/turns" `
    -ContentType "application/json" `
    -Body (@{ answer = $answer } | ConvertTo-Json -Compress)

  $detail = Invoke-RestMethod -Method Get -Uri "$api/v1/mobile/sessions/$($bootstrap.sessionId)"

  if (-not $detail.turns -or $detail.turns.Count -lt 1) {
    throw "Expected turns for feedback UI"
  }
  if ($null -eq $detail.scores.readiness) {
    throw "Expected scores.readiness for feedback UI"
  }
  if (-not $detail.currentQuestion) {
    throw "Expected currentQuestion for stage panel"
  }

  Write-Host "smoke-r1-flow: OK"
  Write-Host "  sessionId=$($bootstrap.sessionId)"
  Write-Host "  readiness=$($detail.scores.readiness) stage=$($detail.stage) turns=$($detail.turns.Count)"
}
finally {
  if ($sessionProc -and -not $sessionProc.HasExited) {
    Stop-Process -Id $sessionProc.Id -Force -ErrorAction SilentlyContinue
  }
  if ($gatewayProc -and -not $gatewayProc.HasExited) {
    Stop-Process -Id $gatewayProc.Id -Force -ErrorAction SilentlyContinue
  }
}
