@echo off
REM 仅启动 Web 前端（需已运行 run-web-stack 中的后端，或自行启动 session + gateway）
cd /d %~dp0..\apps\web
set VITE_DEV_API=http://127.0.0.1:8090
echo Quest English Web — 需后端: scripts\run-web-stack.cmd
echo 默认 API 代理: %VITE_DEV_API%
C:\Users\Administrator\AppData\Roaming\npm\pnpm.cmd dev -- --port 5174 --host 127.0.0.1
