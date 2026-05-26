@echo off
setlocal EnableExtensions
cd /d "%~dp0"

set "SOURCE=example\source"
set "OUT=output\site"
set "BASE_URL=/"
set "SITE_NAME=文档"
set "SITE_URL="
set "LOG="

set "SYNC=release\bin\docserver-sync.exe"
set "EXTRA="
if defined SITE_URL set "EXTRA=--site-url %SITE_URL%"
if defined LOG set "EXTRA=%EXTRA% --log "%LOG%""

"%SYNC%" -s "%SOURCE%" -o "%OUT%" --base-url %BASE_URL% --site-name "%SITE_NAME%" %EXTRA% --watch
exit /b %errorlevel%
