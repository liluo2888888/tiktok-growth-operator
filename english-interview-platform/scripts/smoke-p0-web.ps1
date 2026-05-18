# P0 Web walkthrough: stack on :8090 / :5174 + Playwright full path.
$ErrorActionPreference = "Stop"

$scriptsDir = $PSScriptRoot
$root = Split-Path $scriptsDir -Parent
$goRoot = "C:\toolchains\go1.24.3-tar\go"
$pnpmCmd = "C:\Users\Administrator\AppData\Roaming\npm\pnpm.cmd"
if (-not (Test-Path $pnpmCmd)) { $pnpmCmd = "pnpm" }

$sessionPort = 8082
$gatewayPort = 8090
$webPort = 5174
$gatewayBase = "http://127.0.0.1:$gatewayPort"
$webBase = "http://127.0.0.1:$webPort"
$sessionFilePath = Join-Path $root "services\session-service\data\sessions.json"

function Stop-PortProcess {
  param([int[]]$Ports)
  $connections = Get-NetTCPConnection -LocalPort $Ports -State Listen -ErrorAction SilentlyContinue
  if (-not $connections) { return }
  $connections | Select-Object -ExpandProperty OwningProcess | Sort-Object -Unique |
    ForEach-Object { Stop-Process -Id $_ -Force -ErrorAction SilentlyContinue }
}

function Wait-HttpOk {
  param([string]$Url, [int]$TimeoutSeconds = 60)
  $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
  while ((Get-Date) -lt $deadline) {
    try {
      $r = Invoke-WebRequest -Uri $Url -UseBasicParsing -TimeoutSec 3
      if ($r.StatusCode -ge 200 -and $r.StatusCode -lt 300) { return }
    } catch { Start-Sleep -Milliseconds 600 }
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

Stop-PortProcess -Ports @($gatewayPort, $sessionPort, $webPort, 5173, 5175)
if (Test-Path $sessionFilePath) { Remove-Item $sessionFilePath -Force }

$sessionProc = $null
$gatewayProc = $null
$viteProc = $null

try {
  $sessionProc = Start-GoService -ScriptName "run-session-service.cmd" -ExtraEnv @{
    SESSION_REPOSITORY_BACKEND = "file"
    SESSION_FILE_PATH          = $sessionFilePath
  }
  $gatewayProc = Start-GoService -ScriptName "run-api-gateway.cmd" -ExtraEnv @{
    API_GATEWAY_ADDR           = ":$gatewayPort"
    SESSION_SERVICE_BASE_URL   = "http://127.0.0.1:$sessionPort"
  }

  Wait-HttpOk "$gatewayBase/healthz"
  Wait-HttpOk "http://127.0.0.1:$sessionPort/healthz"

  $webDir = Join-Path $root "apps\web"
  $viteProc = Start-Process -FilePath "cmd.exe" -ArgumentList @(
    "/c",
    "set VITE_DEV_API=$gatewayBase&& set WEB_PORT=$webPort&& ""$pnpmCmd"" dev"
  ) -WorkingDirectory $webDir -WindowStyle Hidden -PassThru

  Wait-HttpOk $webBase

  Push-Location $webDir
  try {
    $env:WALKTHROUGH_BASE = $webBase
    & node .\scripts\walkthrough.mjs
    if ($LASTEXITCODE -ne 0) { throw "walkthrough.mjs failed with exit $LASTEXITCODE" }
  } finally {
    Pop-Location
  }

  Write-Host "smoke-p0-web: OK ($webBase)"
}
finally {
  foreach ($proc in @($viteProc, $gatewayProc, $sessionProc)) {
    if ($proc -and -not $proc.HasExited) {
      Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue
    }
  }
}
