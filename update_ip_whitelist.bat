@echo off
chcp 65001 >nul
echo 🔍 检查IP地址变化...
echo.

cd /d "%~dp0"
venv\Scripts\python.exe check_ip.py

echo.
echo ⏰ %date% %time%
echo 📝 如果IP发生变化，请按照提示更新QQ机器人白名单
echo.
pause
