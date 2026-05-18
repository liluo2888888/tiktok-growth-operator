# Simulates post-ASR text submit through the same mobile turn API the voice pipeline uses.
$ErrorActionPreference = "Stop"

$scriptsDir = $PSScriptRoot
$root = Split-Path $scriptsDir -Parent
$sessionServiceDir = Join-Path $root "services\session-service"
$sessionFilePath = Join-Path $sessionServiceDir "data\sessions.json"
$goRoot = "C:\toolchains\go1.24.3-tar\go"
$apiGatewayBaseURL = "http://localhost:8080"

function Stop-PortProcess {
  param([int[]]$Ports)

  $connections = Get-NetTCPConnection -LocalPort $Ports -State Listen -ErrorAction SilentlyContinue
  if (-not $connections) {
    return
  }

  $connections |
    Select-Object -ExpandProperty OwningProcess |
    Sort-Object -Unique |
    ForEach-Object {
      Stop-Process -Id $_ -Force -ErrorAction SilentlyContinue
    }
}

function Wait-HttpOk {
  param(
    [string]$Url,
    [int]$TimeoutSeconds = 40
  )

  $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
  while ((Get-Date) -lt $deadline) {
    try {
      $response = Invoke-WebRequest -Uri $Url -UseBasicParsing -TimeoutSec 2
      if ($response.StatusCode -eq 200) {
        return
      }
    } catch {
      Start-Sleep -Milliseconds 500
    }
  }

  throw "Timeout waiting for $Url"
}

function Start-GoService {
  param(
    [string]$ScriptName,
    [hashtable]$ExtraEnv = @{}
  )

  $envBlock = @(
    "set ""GOROOT=$goRoot""",
    "set ""PATH=$($goRoot)\bin;%PATH%"""
  )

  foreach ($pair in $ExtraEnv.GetEnumerator()) {
    $envBlock += "set ""$($pair.Key)=$($pair.Value)"""
  }

  $fullCommand = ($envBlock + @("call .\$ScriptName")) -join " && "
  return Start-Process -FilePath "cmd.exe" -ArgumentList "/c", $fullCommand -WorkingDirectory $scriptsDir -WindowStyle Hidden -PassThru
}

Stop-PortProcess -Ports @(8080, 8082)

if (Test-Path $sessionFilePath) {
  Remove-Item $sessionFilePath -Force
}

$sessionProc = $null
$gatewayProc = $null

try {
  $sessionProc = Start-GoService -ScriptName "run-session-service.cmd" -ExtraEnv @{
    SESSION_REPOSITORY_BACKEND = "file"
    SESSION_FILE_PATH          = $sessionFilePath
  }

  $gatewayProc = Start-GoService -ScriptName "run-api-gateway.cmd"

  Wait-HttpOk -Url "http://localhost:8082/healthz"
  Wait-HttpOk -Url "$apiGatewayBaseURL/healthz"

  $bootstrapBody = @{
    roleId    = "product"
    missionId = "behavioral"
  } | ConvertTo-Json -Compress

  $bootstrap = Invoke-RestMethod -Method Post -Uri ($apiGatewayBaseURL + "/v1/mobile/session/bootstrap") -ContentType "application/json" -Body $bootstrapBody

  $turnBody = @{
    answer = "I led a cross functional team to ship a customer facing feature on time."
  } | ConvertTo-Json -Compress

  $submitted = Invoke-RestMethod -Method Post -Uri ($apiGatewayBaseURL + "/v1/mobile/sessions/" + $bootstrap.sessionId + "/turns") -ContentType "application/json" -Body $turnBody
  $detail = Invoke-RestMethod -Method Get -Uri ($apiGatewayBaseURL + "/v1/mobile/sessions/" + $bootstrap.sessionId)

  if (-not $submitted.turns -or $submitted.turns.Count -lt 1) {
    throw "Expected at least one turn after voice-style text submit"
  }

  if (-not $detail.currentQuestion) {
    throw "Expected currentQuestion in session detail"
  }

  if (-not $detail.stage) {
    throw "Expected stage in session detail"
  }

  Write-Host "smoke-voice-turn: OK sessionId=$($bootstrap.sessionId) turns=$($submitted.turns.Count) stage=$($detail.stage)"
}
finally {
  if ($sessionProc -and -not $sessionProc.HasExited) {
    Stop-Process -Id $sessionProc.Id -Force -ErrorAction SilentlyContinue
  }

  if ($gatewayProc -and -not $gatewayProc.HasExited) {
    Stop-Process -Id $gatewayProc.Id -Force -ErrorAction SilentlyContinue
  }
}
