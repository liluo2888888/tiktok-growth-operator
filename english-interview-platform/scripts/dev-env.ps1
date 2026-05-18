$ErrorActionPreference = "Stop"

$goRoot = "C:\toolchains\go1.24.3-tar\go"
$goBin = Join-Path $goRoot "bin"
$pnpmCmd = "C:\Users\Administrator\AppData\Roaming\npm\pnpm.cmd"

$env:GOROOT = $goRoot
if ($env:PATH -notlike "*$goBin*") {
  $env:PATH = "$goBin;$env:PATH"
}

Write-Output "GOROOT=$($env:GOROOT)"
Write-Output "go=$(Get-Command go | Select-Object -ExpandProperty Source)"
Write-Output "pnpm=$pnpmCmd"
