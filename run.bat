@echo off
setlocal
title Chhand - Hindi Poetry and Meter Studio

echo ===================================================
echo   CHHAND - Hindi Poetry and Meter Studio
echo ===================================================
echo.

cd /d "%~dp0"

:: 1. Check Python
where python >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Python was not found in your PATH.
    echo Please install Python 3.11 or newer from https://www.python.org/
    pause
    exit /b 1
)

:: 2. Activate virtual environment if present
if exist ".venv\Scripts\activate.bat" (
    echo [*] Activating .venv...
    call ".venv\Scripts\activate.bat"
) else if exist "venv\Scripts\activate.bat" (
    echo [*] Activating venv...
    call "venv\Scripts\activate.bat"
)

:: 3. Run offline meter check on sample couplet
echo [*] Verifying meter engine with sample couplet...
python scripts\check_meter.py "मन का दीपक जब जले" doha
if %ERRORLEVEL% neq 0 (
    echo [!] Installing required dependencies...
    python -m pip install -r requirements.txt
)

echo.
echo ===================================================
echo   Chhand Studio is running!
echo   Local URL: http://127.0.0.1:8000
echo   API Docs:  http://127.0.0.1:8000/docs
echo   Press CTRL+C to stop the server.
echo ===================================================
echo.

:: 4. Launch default web browser after 2 seconds
start "" cmd /c "timeout /t 2 /nobreak >nul & start http://127.0.0.1:8000"

:: 5. Start Uvicorn server
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

pause
