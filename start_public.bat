@echo off
chcp 65001 >nul
echo ========================================
echo   Xilo AI Tutor - Public Access Mode
echo ========================================
echo.

REM Check if cloudflared is installed
where cloudflared >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ❌ ERROR: cloudflared not found!
    echo.
    echo Please install with:
    echo   winget install Cloudflare.cloudflared
    echo.
    pause
    exit /b 1
)

echo ✅ cloudflared found
echo.

REM Check if in correct directory
if not exist "app.py" (
    echo ❌ ERROR: app.py not found!
    echo Please run this script from the xilov5 directory.
    pause
    exit /b 1
)

echo [1/3] Starting Xilo AI Tutor backend...
echo.
start "Xilo Backend" cmd /k "conda activate llm && python app.py --model llama31"

echo [2/3] Waiting for backend to start (30 seconds)...
echo       The backend window will open separately.
timeout /t 30 /nobreak >nul

echo [3/3] Creating public Cloudflare Tunnel...
echo.
echo ==========================================
echo   📋 COPY THE HTTPS URL BELOW AND SHARE!
echo ==========================================
echo.
cloudflared tunnel --url http://localhost:5000

echo.
echo ==========================================
echo   Tunnel closed. 
echo   Backend is still running in other window.
echo   Close that window to stop the backend.
echo ==========================================
pause
