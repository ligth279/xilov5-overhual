@echo off
REM Xilo AI Tutor - Startup Script for Windows
REM Optimized for Intel GPU with XMX engines

echo.
echo  ██╗  ██╗██╗██╗      ██████╗     ██╗   ██╗███████╗
echo  ╚██╗██╔╝██║██║     ██╔═══██╗    ██║   ██║██╔════╝
echo   ╚███╔╝ ██║██║     ██║   ██║    ██║   ██║███████╗
echo   ██╔██╗ ██║██║     ██║   ██║    ██║   ██║╚════██║
echo  ██╔╝ ██╗██║███████╗╚██████╔╝    ╚██████╔╝███████║
echo  ╚═╝  ╚═╝╚═╝╚══════╝ ╚═════╝      ╚═════╝ ╚══════╝
echo.
echo  🎓 AI Tutor powered by Intel GPU ^& Phi 3.5
echo  🚀 Optimized for XMX engines (Battlemage)
echo.

REM Check if virtual environment exists
if not exist ".venv\Scripts\python.exe" (
    echo ❌ Virtual environment not found!
    echo Please run: python -m venv .venv
    pause
    exit /b 1
)

echo 🔧 Starting Xilo AI Tutor...
echo 📍 Using virtual environment: .venv
echo.

REM Run the application
".venv\Scripts\python.exe" app.py

pause
