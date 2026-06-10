@echo off
chcp 65001 >nul 2>&1
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" call "%~dp0update.bat"

set PORT=8000
set PY=%~dp0.venv\Scripts\python.exe
set SITE_NAME=Docserver Example

echo [1/4] Initial build (example\source -^> dist)...
if exist "dist" rmdir /s /q "dist"
"%PY%" src -s example\source -o dist --site-name "%SITE_NAME%"
if errorlevel 1 (
  echo Build failed.
  pause
  exit /b 1
)

echo [2/4] Watch example\source + theme\ + src\ in background...
echo      UI/theme changes need this watch or re-run example.bat; then Ctrl+F5 in browser.
start "docserver-watch" /b /d "%~dp0" "%PY%" src -s example\source -o dist -v --site-name "%SITE_NAME%" --watch --skip-initial

echo [3/4] Open http://127.0.0.1:%PORT%/  (hard refresh Ctrl+F5 after rebuild)
start "" "http://127.0.0.1:%PORT%/"

echo [4/4] Static server http.server, Ctrl+C to stop
"%PY%" -m http.server %PORT% --bind 127.0.0.1 --directory dist
