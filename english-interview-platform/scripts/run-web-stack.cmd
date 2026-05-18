@echo off
REM Quest English — 一键启动 Web 全栈（session + gateway + Vite）
cd /d %~dp0
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0run-web-stack.ps1" %*
