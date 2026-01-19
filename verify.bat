@echo off
setlocal enabledelayedexpansion

:: ============================================================================
:: AI Vision Overlay - Project Verification Script
:: ============================================================================
:: Checks syntax, imports and project completeness
:: ============================================================================

color 0E
echo.
echo ================================================================
echo       AI VISION OVERLAY - PROJECT VERIFICATION
echo              Checking syntax and completeness
echo ================================================================
echo.

set ERRORS=0
set WARNINGS=0

:: ============================================================================
:: STEP 1: Check Python
:: ============================================================================
echo [1/7] Checking Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found!
    set /a ERRORS+=1
) else (
    for /f "tokens=2" %%a in ('python --version') do echo [OK] Python %%a
)
echo.

:: ============================================================================
:: STEP 2: Check project structure
:: ============================================================================
echo [2/7] Checking project structure...

set REQUIRED_DIRS=src src\core src\modules src\ui src\utils src\plugins profiles docs tests
set MISSING_DIRS=0

for %%d in (%REQUIRED_DIRS%) do (
    if not exist "%%d" (
        echo [ERROR] Missing folder: %%d
        set /a MISSING_DIRS+=1
        set /a ERRORS+=1
    )
)

if !MISSING_DIRS! equ 0 (
    echo [OK] All required folders exist
) else (
    echo [ERROR] Missing !MISSING_DIRS! folders
)
echo.

:: ============================================================================
:: STEP 3: Check Python syntax
:: ============================================================================
echo [3/7] Checking Python syntax...

echo   Checking src/core...
python -m py_compile src\core\*.py 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Syntax errors in src\core
    set /a ERRORS+=1
) else (
    echo [OK] src\core - OK
)

echo   Checking src\modules...
python -m py_compile src\modules\*.py 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Syntax errors in src\modules
    set /a ERRORS+=1
) else (
    echo [OK] src\modules - OK
)

echo   Checking src\utils...
python -m py_compile src\utils\*.py 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Syntax errors in src\utils
    set /a ERRORS+=1
) else (
    echo [OK] src\utils - OK
)

echo   Checking src\ui...
python -m py_compile src\ui\*.py 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Syntax errors in src\ui
    set /a ERRORS+=1
) else (
    echo [OK] src\ui - OK
)
echo.

:: ============================================================================
:: STEP 4: Check required files
:: ============================================================================
echo [4/7] Checking required files...

set REQUIRED_FILES=README.md requirements.txt setup.py build.bat run.bat LICENSE
set MISSING_FILES=0

for %%f in (%REQUIRED_FILES%) do (
    if not exist "%%f" (
        echo [ERROR] Missing file: %%f
        set /a MISSING_FILES+=1
        set /a ERRORS+=1
    )
)

if !MISSING_FILES! equ 0 (
    echo [OK] All required files exist
) else (
    echo [ERROR] Missing !MISSING_FILES! files
)
echo.

:: ============================================================================
:: STEP 5: Check Python modules
:: ============================================================================
echo [5/7] Checking Python modules...

set CORE_MODULES=types config main pipeline
set MODULE_ERRORS=0

for %%m in (%CORE_MODULES%) do (
    if not exist "src\core\%%m.py" (
        echo [ERROR] Missing module: src\core\%%m.py
        set /a MODULE_ERRORS+=1
        set /a ERRORS+=1
    )
)

if !MODULE_ERRORS! equ 0 (
    echo [OK] All core modules exist
) else (
    echo [ERROR] Missing !MODULE_ERRORS! core modules
)

set SYSTEM_MODULES=capture preprocessor ai_vision ocr scene_understanding event_engine decision_manager overlay
set MODULE_ERRORS=0

for %%m in (%SYSTEM_MODULES%) do (
    if not exist "src\modules\%%m.py" (
        echo [ERROR] Missing module: src\modules\%%m.py
        set /a MODULE_ERRORS+=1
        set /a ERRORS+=1
    )
)

if !MODULE_ERRORS! equ 0 (
    echo [OK] All system modules exist
) else (
    echo [ERROR] Missing !MODULE_ERRORS! system modules
)
echo.

:: ============================================================================
:: STEP 6: Check profiles and documentation
:: ============================================================================
echo [6/7] Checking documentation and profiles...

if not exist "docs\README_PL.md" (
    echo [WARNING] Missing docs\README_PL.md
    set /a WARNINGS+=1
) else (
    echo [OK] Polish documentation
)

if not exist "docs\GPU_SUPPORT_PL.md" (
    echo [WARNING] Missing docs\GPU_SUPPORT_PL.md
    set /a WARNINGS+=1
) else (
    echo [OK] GPU documentation
)

if not exist "profiles\darksouls3.yaml" (
    echo [WARNING] Missing example profile darksouls3
    set /a WARNINGS+=1
) else (
    echo [OK] Example profiles
)
echo.

:: ============================================================================
:: STEP 7: Project statistics
:: ============================================================================
echo [7/7] Project statistics...
echo.

:: Count Python files
set PY_COUNT=0
for /r src %%f in (*.py) do set /a PY_COUNT+=1
echo   Python files: !PY_COUNT!

:: Count documentation files
set DOC_COUNT=0
for %%f in (docs\*.md) do set /a DOC_COUNT+=1
echo   Documentation files: !DOC_COUNT!

echo.

:: ============================================================================
:: SUMMARY
:: ============================================================================
echo.
echo ================================================================

if !ERRORS! equ 0 (
    if !WARNINGS! equ 0 (
        echo            VERIFICATION COMPLETED SUCCESSFULLY
        echo ================================================================
        echo.
        echo [SUCCESS] Project is complete and ready to use!
        echo.
        echo [OK] No critical errors
        echo [OK] No warnings
        echo [OK] All modules present
        echo [OK] Syntax correct
    ) else (
        echo             VERIFICATION WITH WARNINGS
        echo ================================================================
        echo.
        echo [WARNING] Found !WARNINGS! warnings
        echo [OK] No critical errors
        echo.
        echo Project is usable, but some optional files may be missing.
    )
) else (
    echo                  VERIFICATION FAILED
    echo ================================================================
    echo.
    echo [ERROR] Found !ERRORS! errors
    if !WARNINGS! gtr 0 (
        echo [WARNING] Found !WARNINGS! warnings
    )
    echo.
    echo [FIX] Fix errors before continuing.
)

echo.
echo ===============================================================
echo.

if !ERRORS! equ 0 (
    echo [NEXT STEPS]
    echo    1. Run: build.bat - to install dependencies
    echo    2. Run: run.bat - to launch application
    echo    3. Check: docs\README_PL.md - documentation
    echo.
) else (
    echo [SUGGESTED ACTIONS]
    echo    1. Check missing files
    echo    2. Fix syntax errors
    echo    3. Run verify.bat again
    echo.
)

echo Press any key to exit...
pause >nul

endlocal
exit /b !ERRORS!
