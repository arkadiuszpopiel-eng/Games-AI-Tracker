@echo off
chcp 65001 >nul 2>&1
setlocal enabledelayedexpansion

:: ============================================================================
:: AI Vision Overlay - Skrypt Uruchamiający
:: ============================================================================
:: Wersja: 1.0.0
:: Opis: Szybkie uruchomienie aplikacji z weryfikacją środowiska
:: ============================================================================

color 0B
echo.
echo ╔════════════════════════════════════════════════════════════════╗
echo ║              AI VISION OVERLAY - URUCHAMIANIE                  ║
echo ║              Gry Jednoosobowe • Zewnętrzna                     ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.

:: ============================================================================
:: Sprawdzenie czy środowisko istnieje
:: ============================================================================
if not exist "venv" (
    echo ❌ BŁĄD: Wirtualne środowisko nie istnieje!
    echo.
    echo 🔧 Najpierw uruchom: build.bat
    echo.
    pause
    exit /b 1
)

:: ============================================================================
:: Aktywacja środowiska
:: ============================================================================
echo [1/4] ⚡ Aktywacja środowiska wirtualnego...
call venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo ❌ BŁĄD: Nie można aktywować środowiska
    echo.
    echo 🔧 Spróbuj uruchomić: build.bat
    echo.
    pause
    exit /b 1
)
echo ✅ Środowisko aktywne
echo.

:: ============================================================================
:: Sprawdzenie zależności
:: ============================================================================
echo [2/4] 🔍 Sprawdzanie zależności...
python -c "import numpy, cv2, yaml" >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️  Brak niektórych zależności
    echo.
    choice /C YN /M "Czy zainstalować brakujące pakiety"
    if !errorlevel! equ 1 (
        echo Instalowanie zależności...
        python -m pip install -r requirements.txt --quiet
        echo ✅ Zależności zainstalowane
    ) else (
        echo ❌ Nie można uruchomić bez wszystkich zależności
        pause
        exit /b 1
    )
) else (
    echo ✅ Wszystkie zależności dostępne
)
echo.

:: ============================================================================
:: Wybór trybu uruchomienia
:: ============================================================================
echo [3/4] 🎯 Wybór trybu uruchomienia...
echo.
echo   1. Panel Sterowania (GUI) - Zalecane
echo   2. Tryb Konsolowy (CLI)
echo   3. Diagnostyka
echo   4. Lista Profili
echo.

choice /C 1234 /M "Wybierz tryb"
set CHOICE=!errorlevel!

echo.

:: ============================================================================
:: Uruchomienie wybranego trybu
:: ============================================================================
echo [4/4] 🚀 Uruchamianie aplikacji...
echo.

if !CHOICE! equ 1 (
    echo 🖥️  Uruchamianie Panelu Sterowania...
    echo.
    python -m ui.control_panel
) else if !CHOICE! equ 2 (
    echo 💻 Uruchamianie w trybie konsolowym...
    echo.
    python -m core.main
) else if !CHOICE! equ 3 (
    echo 🔧 Tryb diagnostyczny...
    echo.
    echo ═══════════════════════════════════════
    echo Python Info:
    python --version
    echo.
    echo Zainstalowane pakiety:
    python -m pip list
    echo.
    echo Testy systemu:
    python -c "from src.core.config import SystemConfig; print('✅ Config OK')"
    python -c "from src.core.types import Entity; print('✅ Types OK')"
    python -c "import numpy, cv2; print('✅ CV2/NumPy OK')"
    echo ═══════════════════════════════════════
    echo.
    pause
) else if !CHOICE! equ 4 (
    echo 📋 Dostępne profile:
    echo.
    python -m core.main --list-profiles
    echo.
    pause
)

if %errorlevel% neq 0 (
    echo.
    echo ❌ Aplikacja zakończyła się z błędem
    echo.
    echo 🔍 Sprawdź logi w folderze logs/
    echo.
    pause
    exit /b 1
)

echo.
echo ═══════════════════════════════════════════════════════════════
echo Aplikacja została zamknięta
echo ═══════════════════════════════════════════════════════════════
echo.

choice /C YN /M "Czy uruchomić ponownie"
if !errorlevel! equ 1 (
    echo.
    echo 🔄 Restartowanie...
    timeout /t 2 >nul
    call run.bat
)

endlocal
