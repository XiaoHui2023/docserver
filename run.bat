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

set "SYNC=%ROOT%release\bin\docserver-sync.exe"
set "EXTRA="
if defined SITE_URL set "EXTRA=--site-url %SITE_URL%"
if defined CACHE_DIR set "EXTRA=%EXTRA% --cache-dir "%CACHE_DIR%""
if defined LOG set "EXTRA=%EXTRA% --log "%LOG%""
if "%WATCH%"=="1" set "EXTRA=%EXTRA% --watch"

"%SYNC%" !SRC_ARGS! -o "%OUT%" --base-url %BASE_URL% --site-name "%SITE_NAME%" %EXTRA%
exit /b %errorlevel%
