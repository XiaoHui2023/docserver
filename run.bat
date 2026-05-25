@echo off
cd /d "%~dp0"
"release\bin\docserver-sync.exe" --watch
exit /b %errorlevel%
