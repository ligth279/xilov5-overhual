# Xilo AI Tutor - PowerShell Startup Script
# Optimized for Intel GPU with XMX engines

Write-Host ""
Write-Host " ██╗  ██╗██╗██╗      ██████╗     ██╗   ██╗███████╗" -ForegroundColor Cyan
Write-Host " ╚██╗██╔╝██║██║     ██╔═══██╗    ██║   ██║██╔════╝" -ForegroundColor Cyan
Write-Host "  ╚███╔╝ ██║██║     ██║   ██║    ██║   ██║███████╗" -ForegroundColor Cyan
Write-Host "  ██╔██╗ ██║██║     ██║   ██║    ██║   ██║╚════██║" -ForegroundColor Cyan
Write-Host " ██╔╝ ██╗██║███████╗╚██████╔╝    ╚██████╔╝███████║" -ForegroundColor Cyan
Write-Host " ╚═╝  ╚═╝╚═╝╚══════╝ ╚═════╝      ╚═════╝ ╚══════╝" -ForegroundColor Cyan
Write-Host ""
Write-Host " 🎓 AI Tutor powered by Intel GPU & Phi 3.5" -ForegroundColor Green
Write-Host " 🚀 Optimized for XMX engines (Battlemage)" -ForegroundColor Green
Write-Host ""

# Check if virtual environment exists
if (-not (Test-Path ".venv\Scripts\python.exe")) {
    Write-Host "❌ Virtual environment not found!" -ForegroundColor Red
    Write-Host "Please run: python -m venv .venv" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "🔧 Starting Xilo AI Tutor..." -ForegroundColor Blue
Write-Host "📍 Using virtual environment: .venv" -ForegroundColor Blue
Write-Host ""

# Run the application
try {
    & ".\.venv\Scripts\python.exe" app.py
}
catch {
    Write-Host "❌ Error starting Xilo AI Tutor: $_" -ForegroundColor Red
    Read-Host "Press Enter to exit"
}
