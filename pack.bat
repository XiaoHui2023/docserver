@echo off
chcp 65001 >nul 2>&1
setlocal EnableExtensions
cd /d "%~dp0"

echo ==^> 在线机打包（需联网）：依赖、vendor、PyInstaller、离线压缩包
echo.

if not exist ".venv\Scripts\python.exe" (
  echo ==^> 创建 .venv
  py -3 -m venv .venv 2>nul || python -m venv .venv
)

set PY=%~dp0.venv\Scripts\python.exe
"%PY%" -V

"%PY%" -m pip install -q -U pip setuptools wheel
"%PY%" -m pip install -q -e ".[dev]"
"%PY%" -m pip install -q "pyinstaller>=6.0"

echo.
echo ==^> 拉取 theme\vendor（mermaid 等）
call "%~dp0tools\fetch-vendor.bat"

echo.
echo ==^> PyInstaller 打包
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"

"%PY%" -m PyInstaller --clean --noconfirm "%~dp0docserver-cli.spec"

echo.
echo ==^> 组装离线压缩包 -^> dist\docserver-offline-win-amd64.zip
call "%~dp0tools\stage-offline.bat"

echo.
echo 完成。产物（均在 dist\）:
echo   dist\docserver-sync.exe
echo   dist\docserver-offline-win-amd64.zip
echo 下一步: 将 zip 拷到离线机解压后运行 run.bat
pause
