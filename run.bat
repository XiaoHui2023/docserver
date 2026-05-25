@echo off
chcp 65001 >nul 2>&1
setlocal EnableExtensions
cd /d "%~dp0"

REM ---------- 默认值（可被 project.yaml 覆盖）----------
set "SOURCE=example\source"
set "OUT=output\site"
set "BASE_URL=/"
set "SITE_NAME=文档"
set "SITE_URL="
REM -----------------------------------------------

if exist "project.yaml" (
  for /f "usebackq eol=# tokens=1,* delims=: " %%a in ("project.yaml") do (
    if /i "%%a"=="source" set "SOURCE=%%b"
    if /i "%%a"=="out" set "OUT=%%b"
    if /i "%%a"=="base_url" set "BASE_URL=%%b"
    if /i "%%a"=="site_name" set "SITE_NAME=%%b"
    if /i "%%a"=="site_url" set "SITE_URL=%%b"
  )
)

if not exist "%SOURCE%" (
  echo 错误: 源目录不存在: %SOURCE%
  echo 请创建并放入 Markdown，或修改本文件顶部 SOURCE。
  exit /b 1
)

if exist "release\bin\docserver-sync.exe" (
  echo ==^> release\bin\docserver-sync.exe
  if "%SITE_URL%"=="" (
    "release\bin\docserver-sync.exe" -s "%SOURCE%" -o "%OUT%" --base-url %BASE_URL% --site-name "%SITE_NAME%" --clean
  ) else (
    "release\bin\docserver-sync.exe" -s "%SOURCE%" -o "%OUT%" --base-url %BASE_URL% --site-name "%SITE_NAME%" --site-url "%SITE_URL%" --clean
  )
  if errorlevel 1 exit /b 1
  goto :done
)

if exist ".venv\Scripts\python.exe" (
  echo ==^> .venv\Scripts\python.exe src
  if "%SITE_URL%"=="" (
    ".venv\Scripts\python.exe" src -s "%SOURCE%" -o "%OUT%" --base-url %BASE_URL% --site-name "%SITE_NAME%" --clean
  ) else (
    ".venv\Scripts\python.exe" src -s "%SOURCE%" -o "%OUT%" --base-url %BASE_URL% --site-name "%SITE_NAME%" --site-url "%SITE_URL%" --clean
  )
  if errorlevel 1 exit /b 1
  goto :done
)

echo 错误: 未找到 release\bin\docserver-sync.exe 且无 .venv
echo 请先在在线机运行 build.bat，或在离线机用 offline-packages 创建 .venv。
exit /b 1

:done
echo.
echo 已构建到: %CD%\%OUT%
echo 部署: 将该目录作为 Web 静态根目录。
pause
