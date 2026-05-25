@echo off
setlocal EnableExtensions
cd /d "%~dp0"

echo ==^> 在线机构建（需联网）：依赖、offline-packages、示例构建、PyInstaller
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
echo ==^> 下载离线 pip 包到 offline-packages\
if exist "offline-packages" rmdir /s /q "offline-packages"
mkdir "offline-packages"
"%PY%" -m pip download -d "offline-packages" ".[dev]"

echo.
echo ==^> 示例构建 -^> output\smoke-test\
if exist "output\smoke-test" rmdir /s /q "output\smoke-test"
mkdir "output" 2>nul
"%PY%" src -S "example\source" -O "output\smoke-test" --site-name "构建检查"

echo.
echo ==^> PyInstaller 打包 -^> release\bin\
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"
if exist "release" rmdir /s /q "release"
mkdir "release\bin"

"%PY%" -m PyInstaller --clean --noconfirm "%~dp0docserver-cli.spec"
copy /y "dist\docserver-sync.exe" "release\bin\docserver-sync.exe" >nul

> "release\README.txt" (
echo docserver 离线运行包
echo.
echo 1. 将整个仓库拷到离线机
echo 2. 编辑 run.bat 顶部 SOURCE、OUT
echo 3. 运行 run.bat，用 Nginx 托管 OUT 目录
echo.
echo 可执行文件: release\bin\docserver-sync.exe
)

echo.
echo 完成。产物:
echo   release\bin\docserver-sync.exe
echo   offline-packages\
echo   output\smoke-test\
echo 下一步: 拷到离线机后运行 run.bat
pause
