@echo off
setlocal EnableExtensions EnableDelayedExpansion
set "ROOT=%~dp0"
cd /d "%ROOT%"

REM SOURCES - one directory per line in the FOR list below
set "SRC_ARGS="
for %%S in (
  demo
) do set "SRC_ARGS=!SRC_ARGS! -s "%%S""

set "OUT=output\site"
set "CACHE_DIR="
set "BASE_URL=/"
set "SITE_NAME=docserver 示例"
set "SITE_URL="
set "LOG="
REM 1=持续监视并重建；0=仅构建一次后退出
set "WATCH=0"

set "EXTRA="
if defined SITE_URL set "EXTRA=--site-url %SITE_URL%"
if defined CACHE_DIR set "EXTRA=%EXTRA% --cache-dir "%CACHE_DIR%""
if defined LOG set "EXTRA=%EXTRA% --log "%LOG%""
if "%WATCH%"=="1" set "EXTRA=%EXTRA% --watch"

set "PIDFILE=%ROOT%.docserver-sync.pid"
set "LIFECYCLE=%ROOT%run-lifecycle.ps1"
set "SYNC=%ROOT%dist\docserver-sync.exe"

if exist "%SYNC%" (
  set "LAUNCH_CMD="%SYNC%" !SRC_ARGS! -o "%OUT%" --base-url %BASE_URL% --site-name "%SITE_NAME%" %EXTRA%"
  goto :run_lifecycle
)

if not exist "%ROOT%.venv\Scripts\python.exe" call "%ROOT%update.bat"
set "PY=%ROOT%.venv\Scripts\python.exe"
if not exist "%PY%" (
  echo 未找到 dist\docserver-sync.exe，且无法创建 .venv。
  echo 开发预览请用 example.bat，或先执行 tools\pack.bat 生成离线包。
  exit /b 1
)

set "LAUNCH_CMD="%PY%" "%ROOT%src" !SRC_ARGS! -o "%OUT%" --base-url %BASE_URL% --site-name "%SITE_NAME%" %EXTRA%"

:run_lifecycle
if not exist "%LIFECYCLE%" (
  echo 未找到 run-lifecycle.ps1
  exit /b 1
)
powershell -NoProfile -ExecutionPolicy Bypass -File "%LIFECYCLE%" -PidFile "%PIDFILE%" -CommandLine "!LAUNCH_CMD!"
exit /b %errorlevel%
