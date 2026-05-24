@echo off
chcp 65001 >nul 2>&1
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" call "%~dp0update.bat"

set PORT=8000
set PY=%~dp0.venv\Scripts\python.exe
set SITE_NAME=Docserver 示例

echo [1/4] 首次构建（确保主题与配置生效）...
"%PY%" src build -S example\source -O dist --site-name "%SITE_NAME%"
if errorlevel 1 (
  echo 构建失败，请检查上方报错。
  pause
  exit /b 1
)

echo [2/4] 后台监视源目录与 theme...
start "docserver-watch" /b /d "%~dp0" "%PY%" src watch -S example\source -O dist -v --site-name "%SITE_NAME%"

echo [3/4] 打开预览 http://127.0.0.1:%PORT%/
start "" "http://127.0.0.1:%PORT%/"

echo [4/4] 静态服务（Ctrl+C 结束；修改源文件后请 Ctrl+F5 强刷浏览器）
".venv\Scripts\python.exe" -m http.server %PORT% --bind 127.0.0.1 --directory dist
