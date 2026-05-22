@echo off
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" call "%~dp0update.bat"
".venv\Scripts\python.exe" src sync -S example\source -O . -v
