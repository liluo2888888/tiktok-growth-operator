@echo off
set GOROOT=C:\toolchains\go1.24.3-tar\go
set PATH=C:\toolchains\go1.24.3-tar\go\bin;%PATH%
cd /d %~dp0..\services\api-gateway
C:\toolchains\go1.24.3-tar\go\bin\go.exe run .\cmd\api\main.go
