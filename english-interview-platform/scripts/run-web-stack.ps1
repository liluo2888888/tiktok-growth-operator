# Quest English — 一键启动 Web 全栈本地开发
# session-service (file, :8082) + api-gateway (:8090) + Vite (:5174)
#
# 用法（仓库根目录或 scripts 目录）:
#   powershell -ExecutionPolicy Bypass -File .\scripts\run-web-stack.ps1
#
# 可选环境变量:
#   WEB_PORT=5174          Vite 端口（默认 5174，避开常被占用的 5173）
#   GATEWAY_PORT=8090      API Gateway 端口（默认 8090，避开常被占用的 8080）
#   SESSION_PORT=8082      Session Service 端口

$ErrorActionPreference = "Stop"

$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$GoRoot = if ($env:GOROOT) { $env:GOROOT } else { "C:\toolchains\go1.24.3-tar\go" }
$GoExe = Join-Path $GoRoot "bin\go.exe"
$PnpmCmd = if (Test-Path "C:\Users\Administrator\AppData\Roaming\npm\pnpm.cmd") {
  "C:\Users\Administrator\AppData\Roaming\npm\pnpm.cmd"
} else {
  "pnpm"
}

$SessionPort = if ($env:SESSION_PORT) { [int]$env:SESSION_PORT } else { 8082 }
$GatewayPort = if ($env:GATEWAY_PORT) { [int]$env:GATEWAY_PORT } else { 8090 }
$WebPort = if ($env:WEB_PORT) { [int]$env:WEB_PORT } else { 5174 }

$env:GOROOT = $GoRoot
$GoBin = Join-Path $GoRoot "bin"
if ($env:PATH -notlike "*$GoBin*") {
  $env:PATH = "$GoBin;$env:PATH"
}

function Test-PortInUse([int]$Port) {
  $conn = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
  return $null -ne $conn
}

function Wait-HttpOk([string]$Url, [int]$TimeoutSec = 45) {
  $deadline = (Get-Date).AddSeconds($TimeoutSec)
  while ((Get-Date) -lt $deadline) {
    try {
      $r = Invoke-WebRequest -Uri $Url -UseBasicParsing -TimeoutSec 3
      if ($r.StatusCode -ge 200 -and $r.StatusCode -lt 300) {
        return $true
      }
    } catch {
      Start-Sleep -Milliseconds 800
    }
  }
  return $false
}

function Start-GoService([string]$Name, [string]$WorkDir) {
  $p = Start-Process -FilePath $GoExe -ArgumentList @("run", ".\cmd\api\main.go") `
    -WorkingDirectory $WorkDir -WindowStyle Minimized -PassThru
  Write-Host "[ok] 已启动 $Name (PID $($p.Id))"
  return $p
}

Write-Host ""
Write-Host "Quest English — Web 全栈启动"
Write-Host "  session-service  -> http://127.0.0.1:$SessionPort  (file 后端)"
Write-Host "  api-gateway      -> http://127.0.0.1:$GatewayPort"
Write-Host "  Vite             -> http://127.0.0.1:$WebPort"
Write-Host ""

if (-not (Test-Path $GoExe)) {
  throw "未找到 Go: $GoExe。请安装 Go 或设置 GOROOT。"
}

# --- Session Service ---
if (Test-PortInUse $SessionPort) {
  Write-Host "[skip] 端口 $SessionPort 已在监听，假定 session-service 已运行"
} else {
  $env:SESSION_REPOSITORY_BACKEND = "file"
  $sessionDir = Join-Path $RepoRoot "services\session-service"
  Push-Location $sessionDir
  try {
    $null = Start-GoService "session-service" $sessionDir
  } finally {
    Pop-Location
  }
  Start-Sleep -Seconds 2
  try {
    $null = Invoke-RestMethod -Uri "http://127.0.0.1:$SessionPort/v1/sessions" -Method POST `
      -ContentType "application/json" -Body '{"roleId":"product","missionId":"self_intro"}' -TimeoutSec 5
    Write-Host "[ok] session-service 就绪"
  } catch {
    Write-Warning "session-service 端口已开但健康检查未通过，请查看最小化窗口中的日志"
  }
}

# --- API Gateway ---
$gatewayBase = "http://127.0.0.1:$GatewayPort"
if (Test-PortInUse $GatewayPort) {
  Write-Host "[skip] 端口 $GatewayPort 已在监听，假定 api-gateway 已运行"
} else {
  $env:API_GATEWAY_ADDR = ":$GatewayPort"
  $env:SESSION_SERVICE_BASE_URL = "http://127.0.0.1:$SessionPort"
  $gatewayDir = Join-Path $RepoRoot "services\api-gateway"
  Push-Location $gatewayDir
  try {
    $null = Start-GoService "api-gateway" $gatewayDir
  } finally {
    Pop-Location
  }
  if (-not (Wait-HttpOk "$gatewayBase/healthz")) {
    throw "api-gateway 未在 ${GatewayPort} 就绪。若 8080 被其他程序占用，请保持 GATEWAY_PORT=8090。"
  }
  Write-Host "[ok] api-gateway 就绪 ($gatewayBase/healthz)"
}

# --- Vite ---
$webDir = Join-Path $RepoRoot "apps\web"
if (-not (Test-Path (Join-Path $webDir "node_modules"))) {
  Write-Host "[..] 首次运行，安装前端依赖…"
  Push-Location $webDir
  try {
    & $PnpmCmd install
    if ($LASTEXITCODE -ne 0) { throw "pnpm install 失败" }
  } finally {
    Pop-Location
  }
}

$env:VITE_DEV_API = $gatewayBase
if (Test-PortInUse $WebPort) {
  Write-Warning "端口 $WebPort 已被占用，Vite 可能自动换端口；请看下方 Local: 行"
}

Write-Host ""
Write-Host "正在启动 Vite（前台，Ctrl+C 结束）…"
Write-Host "浏览器打开: http://127.0.0.1:$WebPort"
Write-Host ""

Push-Location $webDir
try {
  & $PnpmCmd dev -- --port $WebPort --host 127.0.0.1
} finally {
  Pop-Location
}
