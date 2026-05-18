# P0 Gate: automated API smokes + Web Playwright + mobile checks.
$ErrorActionPreference = "Stop"

$scriptsDir = $PSScriptRoot
$root = Split-Path $scriptsDir -Parent
$pnpmCmd = "C:\Users\Administrator\AppData\Roaming\npm\pnpm.cmd"
if (-not (Test-Path $pnpmCmd)) { $pnpmCmd = "pnpm" }

Write-Host "=== P0 Gate automated checks ==="

& "$scriptsDir\smoke-r1-flow.ps1"
& "$scriptsDir\smoke-passport-stamps.ps1"
& "$scriptsDir\smoke-analytics-events.ps1"
& "$scriptsDir\smoke-p0-web.ps1"

Write-Host ""
Write-Host "[..] apps/web typecheck + build"
Push-Location (Join-Path $root "apps\web")
try {
  & $pnpmCmd typecheck
  if ($LASTEXITCODE -ne 0) { throw "web typecheck failed" }
  & $pnpmCmd build
  if ($LASTEXITCODE -ne 0) { throw "web build failed" }
} finally {
  Pop-Location
}

Write-Host "[..] apps/mobile typecheck + test"
Push-Location (Join-Path $root "apps\mobile")
try {
  & $pnpmCmd typecheck
  if ($LASTEXITCODE -ne 0) { throw "mobile typecheck failed" }
  & $pnpmCmd test
  if ($LASTEXITCODE -ne 0) { throw "mobile test failed" }
} finally {
  Pop-Location
}

Write-Host ""
Write-Host "P0 Gate: ALL PASSED (API + Web walkthrough + web/mobile checks)"
Write-Host "Optional manual: legal copy review on /legal"
