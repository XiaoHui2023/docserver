@echo off
chcp 65001 >nul 2>&1
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" call "%~dp0update.bat"

set PORT=8000
set PY=%~dp0.venv\Scripts\python.exe
set SITE_NAME=Docserver Example

echo [1/4] Initial build...
"%PY%" src build -S example\source -O dist --site-name "%SITE_NAME%"
if errorlevel 1 (
  echo Build failed.
  pause
  exit /b 1
)

echo [2/4] Watch source in background (incremental rebuild)...
start "docserver-watch" /b /d "%~dp0" "%PY%" src watch -S example\source -O dist -v --site-name "%SITE_NAME%" --skip-initial

echo [3/4] Open http://127.0.0.1:%PORT%/  (refresh browser after edits)
start "" "http://127.0.0.1:%PORT%/"

echo [4/4] Static server http.server, Ctrl+C to stop
"%PY%" -m http.server %PORT% --bind 127.0.0.1 --directory dist
