@echo off
setlocal EnableExtensions
cd /d "%~dp0"

REM ---------- 按需修改（路径相对仓库根）----------
set "SOURCE=docs"
set "OUT=output\site"
set "BASE_URL=/"
set "SITE_NAME=文档"
set "SITE_URL="
REM -----------------------------------------------

if not exist "%SOURCE%" (
  echo 错误: 源目录不存在: %SOURCE%
  echo 请创建并放入 Markdown，或修改本文件顶部 SOURCE。
  exit /b 1
)

if exist "release\bin\docserver-sync.exe" (
  echo ==^> release\bin\docserver-sync.exe
  if "%SITE_URL%"=="" (
    "release\bin\docserver-sync.exe" -S "%SOURCE%" -O "%OUT%" --base-url %BASE_URL% --site-name "%SITE_NAME%" --clean
  ) else (
    "release\bin\docserver-sync.exe" -S "%SOURCE%" -O "%OUT%" --base-url %BASE_URL% --site-name "%SITE_NAME%" --site-url "%SITE_URL%" --clean
  )
  goto :done
)

if exist ".venv\Scripts\python.exe" (
  echo ==^> .venv\python src
  if "%SITE_URL%"=="" (
    ".venv\Scripts\python.exe" src -S "%SOURCE%" -O "%OUT%" --base-url %BASE_URL% --site-name "%SITE_NAME%" --clean
  ) else (
    ".venv\Scripts\python.exe" src -S "%SOURCE%" -O "%OUT%" --base-url %BASE_URL% --site-name "%SITE_NAME%" --site-url "%SITE_URL%" --clean
  )
  goto :done
)

echo 错误: 未找到 release\bin\docserver-sync.exe 且无 .venv
echo 请先在在线机运行 build.bat，或在离线机用 offline-packages 创建 .venv。
exit /b 1

:done
echo.
echo 已构建到: %~dp0%OUT%
echo 部署: 将该目录作为 Web 静态根目录。
pause
