# Chhand PowerShell Runner
Write-Host "===================================================" -ForegroundColor Cyan
Write-Host "  CHHAND (छंद) - Hindi Poetry & Meter Studio" -ForegroundColor Cyan
Write-Host "===================================================" -ForegroundColor Cyan
Write-Host ""

Set-Location $PSScriptRoot

# Check Python
$pythonCmd = Get-Command python -ErrorAction SilentlyContinue
if (-not $pythonCmd) {
    Write-Host "[ERROR] Python was not found in your PATH." -ForegroundColor Red
    Write-Host "Please install Python 3.11 or newer from https://www.python.org/"
    pause
    exit 1
}

# Activate virtual environment if present
if (Test-Path ".\.venv\Scripts\Activate.ps1") {
    Write-Host "[*] Activating .venv..." -ForegroundColor Yellow
    & ".\.venv\Scripts\Activate.ps1"
} elseif (Test-Path ".\venv\Scripts\Activate.ps1") {
    Write-Host "[*] Activating venv..." -ForegroundColor Yellow
    & ".\venv\Scripts\Activate.ps1"
}

# Verify meter engine
Write-Host "[*] Verifying meter engine with sample couplet..." -ForegroundColor Yellow
python scripts\check_meter.py "मन का दीपक जब जले" doha

Write-Host ""
Write-Host "===================================================" -ForegroundColor Green
Write-Host "  Chhand Studio is running!" -ForegroundColor Green
Write-Host "  Local URL: http://127.0.0.1:8000" -ForegroundColor White
Write-Host "  API Docs:  http://127.0.0.1:8000/docs" -ForegroundColor White
Write-Host "  Press CTRL+C in this terminal to stop." -ForegroundColor Gray
Write-Host "===================================================" -ForegroundColor Green
Write-Host ""

# Launch web browser
Start-Process "http://127.0.0.1:8000"

# Start Uvicorn
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
