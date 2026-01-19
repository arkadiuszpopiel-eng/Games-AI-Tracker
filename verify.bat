@echo off
chcp 65001 >nul 2>&1
setlocal enabledelayedexpansion

:: ============================================================================
:: AI Vision Overlay - Skrypt Weryfikacyjny
:: ============================================================================
:: Sprawdza składnię, importy i kompletność projektu
:: ============================================================================

color 0E
echo.
echo ╔════════════════════════════════════════════════════════════════╗
echo ║         AI VISION OVERLAY - WERYFIKACJA PROJEKTU               ║
echo ║              Sprawdzanie składni i kompletności                ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.

set ERRORS=0
set WARNINGS=0

:: ============================================================================
:: KROK 1: Sprawdzenie Python
:: ============================================================================
echo [1/7] 🐍 Sprawdzanie Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python nie znaleziony!
    set /a ERRORS+=1
) else (
    for /f "tokens=2" %%a in ('python --version') do echo ✅ Python %%a
)
echo.

:: ============================================================================
:: KROK 2: Sprawdzenie struktury projektu
:: ============================================================================
echo [2/7] 📁 Sprawdzanie struktury projektu...

set REQUIRED_DIRS=src src\core src\modules src\ui src\utils src\plugins profiles docs tests
set MISSING_DIRS=0

for %%d in (%REQUIRED_DIRS%) do (
    if not exist "%%d" (
        echo ❌ Brak folderu: %%d
        set /a MISSING_DIRS+=1
        set /a ERRORS+=1
    )
)

if !MISSING_DIRS! equ 0 (
    echo ✅ Wszystkie wymagane foldery istnieją
) else (
    echo ❌ Brak !MISSING_DIRS! folderów
)
echo.

:: ============================================================================
:: KROK 3: Sprawdzenie składni Python
:: ============================================================================
echo [3/7] ✔️  Sprawdzanie składni Python...

echo   Sprawdzanie src/core...
python -m py_compile src\core\*.py 2>nul
if %errorlevel% neq 0 (
    echo ❌ Błędy składni w src\core
    set /a ERRORS+=1
) else (
    echo ✅ src\core - OK
)

echo   Sprawdzanie src\modules...
python -m py_compile src\modules\*.py 2>nul
if %errorlevel% neq 0 (
    echo ❌ Błędy składni w src\modules
    set /a ERRORS+=1
) else (
    echo ✅ src\modules - OK
)

echo   Sprawdzanie src\utils...
python -m py_compile src\utils\*.py 2>nul
if %errorlevel% neq 0 (
    echo ❌ Błędy składni w src\utils
    set /a ERRORS+=1
) else (
    echo ✅ src\utils - OK
)

echo   Sprawdzanie src\ui...
python -m py_compile src\ui\*.py 2>nul
if %errorlevel% neq 0 (
    echo ❌ Błędy składni w src\ui
    set /a ERRORS+=1
) else (
    echo ✅ src\ui - OK
)
echo.

:: ============================================================================
:: KROK 4: Sprawdzenie wymaganych plików
:: ============================================================================
echo [4/7] 📄 Sprawdzanie wymaganych plików...

set REQUIRED_FILES=README.md requirements.txt setup.py build.bat run.bat LICENSE
set MISSING_FILES=0

for %%f in (%REQUIRED_FILES%) do (
    if not exist "%%f" (
        echo ❌ Brak pliku: %%f
        set /a MISSING_FILES+=1
        set /a ERRORS+=1
    )
)

if !MISSING_FILES! equ 0 (
    echo ✅ Wszystkie wymagane pliki istnieją
) else (
    echo ❌ Brak !MISSING_FILES! plików
)
echo.

:: ============================================================================
:: KROK 5: Sprawdzenie modułów Python
:: ============================================================================
echo [5/7] 🔧 Sprawdzanie modułów Python...

set CORE_MODULES=types config main pipeline
set MODULE_ERRORS=0

for %%m in (%CORE_MODULES%) do (
    if not exist "src\core\%%m.py" (
        echo ❌ Brak modułu: src\core\%%m.py
        set /a MODULE_ERRORS+=1
        set /a ERRORS+=1
    )
)

if !MODULE_ERRORS! equ 0 (
    echo ✅ Wszystkie moduły core istnieją
) else (
    echo ❌ Brak !MODULE_ERRORS! modułów core
)

set SYSTEM_MODULES=capture preprocessor ai_vision ocr scene_understanding event_engine decision_manager overlay
set MODULE_ERRORS=0

for %%m in (%SYSTEM_MODULES%) do (
    if not exist "src\modules\%%m.py" (
        echo ❌ Brak modułu: src\modules\%%m.py
        set /a MODULE_ERRORS+=1
        set /a ERRORS+=1
    )
)

if !MODULE_ERRORS! equ 0 (
    echo ✅ Wszystkie moduły systemowe istnieją
) else (
    echo ❌ Brak !MODULE_ERRORS! modułów systemowych
)
echo.

:: ============================================================================
:: KROK 6: Sprawdzenie profili i dokumentacji
:: ============================================================================
echo [6/7] 📚 Sprawdzanie dokumentacji i profili...

if not exist "docs\README_PL.md" (
    echo ⚠️  Brak docs\README_PL.md
    set /a WARNINGS+=1
) else (
    echo ✅ Dokumentacja polska
)

if not exist "docs\GPU_SUPPORT_PL.md" (
    echo ⚠️  Brak docs\GPU_SUPPORT_PL.md
    set /a WARNINGS+=1
) else (
    echo ✅ Dokumentacja GPU
)

if not exist "profiles\darksouls3.yaml" (
    echo ⚠️  Brak przykładowego profilu darksouls3
    set /a WARNINGS+=1
) else (
    echo ✅ Profile przykładowe
)
echo.

:: ============================================================================
:: KROK 7: Statystyki projektu
:: ============================================================================
echo [7/7] 📊 Statystyki projektu...
echo.

:: Zlicz pliki Python
set PY_COUNT=0
for /r src %%f in (*.py) do set /a PY_COUNT+=1
echo   Plików Python: !PY_COUNT!

:: Zlicz linie kodu
if exist src\core\*.py (
    powershell -command "& {(Get-Content src\core\*.py | Measure-Object -Line).Lines}" >lines.tmp 2>nul
    if exist lines.tmp (
        set /p LINES=<lines.tmp
        echo   Linii kodu (core): !LINES!
        del lines.tmp
    )
)

:: Zlicz pliki dokumentacji
set DOC_COUNT=0
for %%f in (docs\*.md) do set /a DOC_COUNT+=1
echo   Plików dokumentacji: !DOC_COUNT!

echo.

:: ============================================================================
:: PODSUMOWANIE
:: ============================================================================
echo.
echo ╔════════════════════════════════════════════════════════════════╗

if !ERRORS! equ 0 (
    if !WARNINGS! equ 0 (
        echo ║              ✅ WERYFIKACJA ZAKOŃCZONA SUKCESEM                ║
        echo ╚════════════════════════════════════════════════════════════════╝
        echo.
        echo 🎉 Projekt jest kompletny i gotowy do użycia!
        echo.
        echo ✅ Brak błędów krytycznych
        echo ✅ Brak ostrzeżeń
        echo ✅ Wszystkie moduły na miejscu
        echo ✅ Składnia poprawna
    ) else (
        echo ║           ⚠️  WERYFIKACJA Z OSTRZEŻENIAMI                     ║
        echo ╚════════════════════════════════════════════════════════════════╝
        echo.
        echo ⚠️  Znaleziono !WARNINGS! ostrzeżeń
        echo ✅ Brak błędów krytycznych
        echo.
        echo Projekt jest użyteczny, ale niektóre opcjonalne pliki mogą brakować.
    )
) else (
    echo ║                ❌ WERYFIKACJA NIEUDANA                          ║
    echo ╚════════════════════════════════════════════════════════════════╝
    echo.
    echo ❌ Znaleziono !ERRORS! błędów
    if !WARNINGS! gtr 0 (
        echo ⚠️  Znaleziono !WARNINGS! ostrzeżeń
    )
    echo.
    echo 🔧 Napraw błędy przed kontynuowaniem.
)

echo.
echo ═══════════════════════════════════════════════════════════════
echo.

if !ERRORS! equ 0 (
    echo 🚀 Następne kroki:
    echo    1. Uruchom: build.bat - aby zainstalować zależności
    echo    2. Uruchom: run.bat - aby uruchomić aplikację
    echo    3. Sprawdź: docs\README_PL.md - dokumentacja
    echo.
) else (
    echo 🔧 Sugerowane działania:
    echo    1. Sprawdź brakujące pliki
    echo    2. Napraw błędy składni
    echo    3. Uruchom verify.bat ponownie
    echo.
)

echo Naciśnij dowolny klawisz aby zakończyć...
pause >nul

endlocal
exit /b !ERRORS!
