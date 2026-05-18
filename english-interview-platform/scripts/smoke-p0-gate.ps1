# P0 Gate: run automated API smokes required before internal beta.
$ErrorActionPreference = "Stop"

$scriptsDir = $PSScriptRoot

Write-Host "=== P0 Gate automated checks ==="

& "$scriptsDir\smoke-r1-flow.ps1"
& "$scriptsDir\smoke-passport-stamps.ps1"
& "$scriptsDir\smoke-analytics-events.ps1"

Write-Host ""
Write-Host "P0 Gate API smokes: ALL PASSED"
Write-Host "Manual still required: Web full path (scripts/run-web.cmd) + legal/onboarding review."
