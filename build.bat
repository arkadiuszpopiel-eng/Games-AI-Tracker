@echo off
chcp 65001 >nul 2>&1
setlocal enabledelayedexpansion

:: ============================================================================
:: AI Vision Overlay - Automatyczny System Budowania
:: ============================================================================
:: Wersja: 1.0.0
:: Opis: Kompletna automatyzacja instalacji i konfiguracji systemu
:: ============================================================================

color 0A
echo.
echo ╔════════════════════════════════════════════════════════════════╗
echo ║          AI VISION OVERLAY - AUTOMATYCZNY BUILD                ║
echo ║                  Klasy Enterprise • Modularna                  ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.

:: ============================================================================
:: KROK 1: Sprawdzenie środowiska Python
:: ============================================================================
echo [1/8] 🔍 Sprawdzanie środowiska Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ BŁĄD: Python nie jest zainstalowany!
    echo.
    echo Pobierz Python 3.10+ z: https://www.python.org/downloads/
    echo Upewnij się, że dodajesz Python do PATH podczas instalacji.
    pause
    exit /b 1
)

for /f "tokens=2" %%a in ('python --version') do set PYTHON_VERSION=%%a
echo ✅ Python %PYTHON_VERSION% znaleziony
echo.

:: Sprawdzenie wersji Python (wymaga 3.10+)
python -c "import sys; exit(0 if sys.version_info >= (3, 10) else 1)" >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ BŁĄD: Wymagany Python 3.10 lub nowszy!
    echo    Obecna wersja: %PYTHON_VERSION%
    pause
    exit /b 1
)

:: ============================================================================
:: KROK 2: Sprawdzenie pip
:: ============================================================================
echo [2/8] 🔍 Sprawdzanie pip...
python -m pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ pip nie znaleziony, instalowanie...
    python -m ensurepip --default-pip
    python -m pip install --upgrade pip
) else (
    echo ✅ pip zainstalowany
    echo.
    echo 📦 Aktualizacja pip...
    python -m pip install --upgrade pip --quiet
)
echo.

:: ============================================================================
:: KROK 3: Utworzenie wirtualnego środowiska
:: ============================================================================
echo [3/8] 🔧 Tworzenie wirtualnego środowiska...
if exist "venv" (
    echo ⚠️  Wirtualne środowisko już istnieje
    choice /C YN /M "Czy chcesz je usunąć i utworzyć na nowo"
    if !errorlevel! equ 1 (
        echo Usuwanie starego środowiska...
        rmdir /s /q venv
        python -m venv venv
        echo ✅ Nowe środowisko utworzone
    ) else (
        echo ℹ️  Używanie istniejącego środowiska
    )
) else (
    python -m venv venv
    echo ✅ Wirtualne środowisko utworzone
)
echo.

:: ============================================================================
:: KROK 4: Aktywacja środowiska
:: ============================================================================
echo [4/8] ⚡ Aktywacja wirtualnego środowiska...
call venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo ❌ BŁĄD: Nie można aktywować środowiska
    pause
    exit /b 1
)
echo ✅ Środowisko aktywne
echo.

:: ============================================================================
:: KROK 5: Instalacja podstawowych narzędzi
:: ============================================================================
echo [5/8] 🛠️  Instalacja podstawowych narzędzi...
echo.
echo   Instalowanie setuptools, wheel...
python -m pip install --upgrade setuptools wheel --quiet
if %errorlevel% neq 0 (
    echo ❌ BŁĄD podczas instalacji narzędzi
    pause
    exit /b 1
)
echo ✅ Narzędzia zainstalowane
echo.

:: ============================================================================
:: KROK 6: Instalacja zależności projektu
:: ============================================================================
echo [6/8] 📦 Instalacja zależności projektu...
echo.
echo   To może potrwać kilka minut...
echo.

if exist "requirements.txt" (
    echo   📄 Instalowanie z requirements.txt...
    python -m pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo ⚠️  Wystąpiły problemy z niektórymi pakietami
        echo    Kontynuowanie instalacji...
    )
) else (
    echo ⚠️  Plik requirements.txt nie znaleziony
)

echo.
echo   📄 Instalowanie projektu w trybie deweloperskim...
python -m pip install -e .
if %errorlevel% neq 0 (
    echo ❌ BŁĄD podczas instalacji projektu
    pause
    exit /b 1
)

echo ✅ Zależności zainstalowane
echo.

:: ============================================================================
:: KROK 7: Pobieranie modeli AI (opcjonalne)
:: ============================================================================
echo [7/8] 🤖 Konfiguracja modeli AI...
echo.

if not exist "models" mkdir models

echo   Pobieranie modelu YOLOv8n...
python -c "from ultralytics import YOLO; model = YOLO('yolov8n.pt')" >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Model YOLOv8n gotowy
) else (
    echo ⚠️  Model będzie pobrany przy pierwszym uruchomieniu
)
echo.

:: ============================================================================
:: KROK 8: Weryfikacja instalacji
:: ============================================================================
echo [8/8] ✔️  Weryfikacja instalacji...
echo.

echo   Sprawdzanie importów...
python -c "import numpy; import cv2; import yaml" >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Podstawowe biblioteki nie zainstalowane poprawnie
    pause
    exit /b 1
)

python -c "import src.core.types; import src.core.config" >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Moduły projektu nie zainstalowane poprawnie
    pause
    exit /b 1
)

echo ✅ Wszystkie moduły zainstalowane poprawnie
echo.

:: ============================================================================
:: URUCHOMIENIE TESTÓW (opcjonalne)
:: ============================================================================
echo.
choice /C YN /M "Czy uruchomić testy jednostkowe"
if !errorlevel! equ 1 (
    echo.
    echo 🧪 Uruchamianie testów...
    python -m pytest tests/ -v --tb=short
    if !errorlevel! equ 0 (
        echo ✅ Wszystkie testy przeszły pomyślnie
    ) else (
        echo ⚠️  Niektóre testy nie powiodły się
        echo    Aplikacja powinna działać, ale sprawdź logi
    )
)

:: ============================================================================
:: PODSUMOWANIE
:: ============================================================================
echo.
echo ╔════════════════════════════════════════════════════════════════╗
echo ║                    ✅ BUILD ZAKOŃCZONY!                         ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.
echo 🎉 System AI Vision Overlay został pomyślnie zbudowany!
echo.
echo 📁 Struktura projektu:
echo    ├─ src/          - Kod źródłowy
echo    ├─ profiles/     - Profile gier
echo    ├─ models/       - Modele AI
echo    ├─ docs/         - Dokumentacja
echo    └─ tests/        - Testy
echo.
echo 🚀 Aby uruchomić aplikację:
echo    • Uruchom: run.bat
echo    • Lub: python -m core.main
echo.
echo 📖 Dokumentacja: docs\README_PL.md
echo 🎮 Profile przykładowe: profiles\darksouls3.yaml
echo.
echo ⚙️  Następne kroki:
echo    1. Sprawdź profile w folderze profiles/
echo    2. Dostosuj konfigurację dla swojej gry
echo    3. Uruchom aplikację: run.bat
echo.

choice /C YN /M "Czy uruchomić aplikację teraz"
if !errorlevel! equ 1 (
    echo.
    echo 🚀 Uruchamianie AI Vision Overlay...
    call run.bat
) else (
    echo.
    echo Możesz uruchomić aplikację później poleceniem: run.bat
)

echo.
echo Naciśnij dowolny klawisz aby zakończyć...
pause >nul

endlocal
