@echo off
setlocal EnableExtensions
set "ROOT=%~dp0.."
cd /d "%ROOT%"

if exist "dist\staging" rmdir /s /q "dist\staging"
mkdir "dist\staging\dist"
copy /y "dist\docserver-sync.exe" "dist\staging\dist\docserver-sync.exe" >nul
copy /y "run.bat" "dist\staging\" >nul
copy /y "run-lifecycle.ps1" "dist\staging\" >nul
xcopy /e /i /q "demo" "dist\staging\demo\" >nul
xcopy /e /i /q "theme" "dist\staging\theme\" >nul
if exist "cache\plugin\privacy" (
  mkdir "dist\staging\cache\plugin" 2>nul
  xcopy /e /i /q "cache\plugin\privacy" "dist\staging\cache\plugin\privacy\" >nul
)

copy /y "%~dp0offline-package-readme.txt" "dist\staging\README.txt" >nul

tar -a -c -f "dist\docserver-offline-win-amd64.zip" -C "dist\staging" .
if exist "dist\staging" rmdir /s /q "dist\staging"
