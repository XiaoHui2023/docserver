@echo off
setlocal EnableExtensions EnableDelayedExpansion
set "ROOT=%~dp0"
cd /d "%ROOT%"

REM SOURCES - one directory per line in the FOR list below (same idea as run.sh)
set "SRC_ARGS="
for %%S in (
  example\source
  other\docs
) do set "SRC_ARGS=!SRC_ARGS! -s "%%S""

set "OUT=output\site"
set "CACHE_DIR="
set "BASE_URL=/"
set "SITE_NAME=文档"
set "SITE_URL="
set "LOG="

set "SYNC=%ROOT%release\bin\docserver-sync.exe"
set "EXTRA="
if defined SITE_URL set "EXTRA=--site-url %SITE_URL%"
if defined CACHE_DIR set "EXTRA=%EXTRA% --cache-dir "%CACHE_DIR%""
if defined LOG set "EXTRA=%EXTRA% --log "%LOG%""

"%SYNC%" !SRC_ARGS! -o "%OUT%" --base-url %BASE_URL% --site-name "%SITE_NAME%" %EXTRA% --watch
exit /b %errorlevel%
