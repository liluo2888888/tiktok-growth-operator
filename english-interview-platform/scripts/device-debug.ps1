# Pre-flight checks for physical device + Expo Go debugging.
$ErrorActionPreference = "Stop"

$scriptsDir = $PSScriptRoot
$root = Split-Path $scriptsDir -Parent

function Get-LanIp {
  $wlan = Get-NetIPAddress -AddressFamily IPv4 -ErrorAction SilentlyContinue |
    Where-Object {
      $_.IPAddress -notlike "127.*" -and
      $_.IPAddress -notlike "169.254.*" -and
      $_.InterfaceAlias -match "WLAN|Wi-?Fi|Ethernet"
    } |
    Sort-Object { if ($_.InterfaceAlias -match "WLAN|Wi-?Fi") { 0 } else { 1 } }

  if ($wlan) {
    return ($wlan | Select-Object -First 1).IPAddress
  }

  return $null
}

function Test-PortListening {
  param([int]$Port)
  return [bool](Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue)
}

function Test-Http {
  param([string]$Url)

  try {
    $response = Invoke-WebRequest -Uri $Url -UseBasicParsing -TimeoutSec 3
    return [pscustomobject]@{ Ok = $true; Status = $response.StatusCode; Error = $null }
  } catch {
    return [pscustomobject]@{ Ok = $false; Status = $null; Error = $_.Exception.Message }
  }
}

$lanIp = Get-LanIp
$envPath = Join-Path $root "apps\mobile\.env"

Write-Host "=== English Interview — device debug ===" -ForegroundColor Cyan
Write-Host ""

if ($lanIp) {
  Write-Host "LAN IP (use in .env): $lanIp" -ForegroundColor Green
} else {
  Write-Host "LAN IP: not detected" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "--- Services (ports) ---"
$gwUp = Test-PortListening -Port 8080
$ssUp = Test-PortListening -Port 8082
Write-Host ("api-gateway :8080  -> " + $(if ($gwUp) { "listening" } else { "NOT running" }))
Write-Host ("session-svc :8082  -> " + $(if ($ssUp) { "listening" } else { "NOT running" }))

Write-Host ""
Write-Host "--- HTTP health ---"
$local = Test-Http "http://localhost:8080/healthz"
Write-Host ("localhost:8080/healthz -> " + $(if ($local.Ok) { "OK $($local.Status)" } else { "FAIL $($local.Error)" }))

if ($lanIp) {
  $remote = Test-Http "http://${lanIp}:8080/healthz"
  Write-Host ("${lanIp}:8080/healthz -> " + $(if ($remote.Ok) { "OK $($remote.Status)" } else { "FAIL $($remote.Error)" }))
  if ($local.Ok -and -not $remote.Ok) {
    Write-Host ""
    Write-Host "Localhost works but LAN IP fails — likely Windows Firewall." -ForegroundColor Yellow
    Write-Host "Run as Administrator:"
    Write-Host '  netsh advfirewall firewall add rule name="English Interview API 8080" dir=in action=allow protocol=TCP localport=8080'
  }
}

Write-Host ""
Write-Host "--- Mobile .env ---"
if (Test-Path $envPath) {
  Get-Content $envPath | ForEach-Object {
    if ($_ -match "OPENAI_API_KEY=(.+)") {
      $key = $Matches[1]
      if ($key -eq "sk-your-key-here" -or [string]::IsNullOrWhiteSpace($key)) {
        Write-Host "EXPO_PUBLIC_OPENAI_API_KEY= (not set — manual transcript only)"
      } else {
        Write-Host "EXPO_PUBLIC_OPENAI_API_KEY= (set, length $($key.Length))"
      }
    } elseif ($_ -match "API_BASE_URL=(.+)") {
      Write-Host $_
      if ($_ -match "localhost|127\.0\.0\.1") {
        Write-Host "  ^ Phone cannot reach localhost — run scripts\setup-device-env.ps1" -ForegroundColor Yellow
      }
    } else {
      if ($_ -notmatch "^\s*#") { Write-Host $_ }
    }
  }
} else {
  Write-Host ".env missing — run: scripts\setup-device-env.ps1" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "--- Checklist ---"
Write-Host "[ ] Phone and PC on same Wi-Fi (not guest network)"
Write-Host "[ ] Expo started AFTER .env was written (restart required)"
Write-Host "[ ] Android: app.json usesCleartextTraffic (HTTP allowed)"
Write-Host "[ ] iOS: NSAllowsLocalNetworking in app.json"
Write-Host "[ ] Grant microphone when prompted"

if (-not $gwUp -or -not $ssUp) {
  exit 1
}

if ($lanIp) {
  $remote = Test-Http "http://${lanIp}:8080/healthz"
  if (-not $remote.Ok) {
    exit 2
  }
}

Write-Host ""
Write-Host "Ready for device smoke." -ForegroundColor Green
