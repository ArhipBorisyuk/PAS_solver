@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo Запускаем EXE из текущей папки...
start "" /wait app_launcher.exe

echo.
echo Если ты видишь это — .exe отработал и закрылся.
pause
