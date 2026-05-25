@echo off
setlocal EnableExtensions
cd /d "%~dp0\.."
set "DEST=theme\javascripts\mermaid.min.js"

if exist "%DEST%" for %%A in ("%DEST%") do if %%~zA gtr 0 exit /b 0

if not exist "theme\javascripts" mkdir "theme\javascripts"
curl.exe -fsSL -o "%DEST%" "https://unpkg.com/mermaid@11/dist/mermaid.min.js"
if errorlevel 1 (
  echo 错误: 下载 mermaid.min.js 失败
  exit /b 1
)
