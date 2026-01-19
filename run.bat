@echo off
setlocal enabledelayedexpansion

:: ============================================================================
:: AI Vision Overlay - Quick Run Script
:: ============================================================================
:: Version: 1.0.0
:: Description: Quick launch with environment verification
:: ============================================================================

color 0B
echo.
echo ================================================================
echo           AI VISION OVERLAY - LAUNCHING
echo           Single-Player Games - External - Safe
echo ================================================================
echo.

:: ============================================================================
:: Check if environment exists
:: ============================================================================
if not exist "venv" (
    echo [ERROR] Virtual environment does not exist!
    echo.
    echo [FIX] Run: build.bat
    echo.
    pause
    exit /b 1
)

:: ============================================================================
:: Activate environment
:: ============================================================================
echo [1/4] Activating virtual environment...
call venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo [ERROR] Cannot activate environment
    echo.
    echo [FIX] Try running: build.bat
    echo.
    pause
    exit /b 1
)
echo [OK] Environment active
echo.

:: ============================================================================
:: Check dependencies
:: ============================================================================
echo [2/4] Checking dependencies...
python -c "import numpy, cv2, yaml" >nul 2>&1
if %errorlevel% neq 0 (
    echo [WARNING] Some dependencies missing
    echo.
    choice /C YN /M "Install missing packages"
    if !errorlevel! equ 1 (
        echo Installing dependencies...
        python -m pip install -r requirements.txt --quiet
        echo [OK] Dependencies installed
    ) else (
        echo [ERROR] Cannot run without all dependencies
        pause
        exit /b 1
    )
) else (
    echo [OK] All dependencies available
)
echo.

:: ============================================================================
:: Select run mode
:: ============================================================================
echo [3/4] Select run mode...
echo.
echo   1. Control Panel (GUI) - Recommended
echo   2. Console Mode (CLI)
echo   3. Diagnostics
echo   4. List Profiles
echo.

choice /C 1234 /M "Select mode"
set CHOICE=!errorlevel!

echo.

:: ============================================================================
:: Launch selected mode
:: ============================================================================
echo [4/4] Launching application...
echo.

if !CHOICE! equ 1 (
    echo [GUI] Launching Control Panel...
    echo.
    python -m ui.control_panel
) else if !CHOICE! equ 2 (
    echo [CLI] Launching console mode...
    echo.
    python -m core.main
) else if !CHOICE! equ 3 (
    echo [DIAG] Diagnostic mode...
    echo.
    echo =======================================
    echo Python Info:
    python --version
    echo.
    echo Installed packages:
    python -m pip list
    echo.
    echo System tests:
    python -c "from src.core.config import SystemConfig; print('[OK] Config')"
    python -c "from src.core.types import Entity; print('[OK] Types')"
    python -c "import numpy, cv2; print('[OK] CV2/NumPy')"
    echo =======================================
    echo.
    pause
) else if !CHOICE! equ 4 (
    echo [PROFILES] Available profiles:
    echo.
    python -m core.main --list-profiles
    echo.
    pause
)

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Application exited with error
    echo.
    echo Check logs in logs/ folder
    echo.
    pause
    exit /b 1
)

echo.
echo ===============================================================
echo Application closed
echo ===============================================================
echo.

choice /C YN /M "Run again"
if !errorlevel! equ 1 (
    echo.
    echo [RESTART] Restarting...
    timeout /t 2 >nul
    call run.bat
)

endlocal
