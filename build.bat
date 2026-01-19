@echo off
setlocal enabledelayedexpansion

:: ============================================================================
:: AI Vision Overlay - Automatic Build System
:: ============================================================================
:: Version: 1.0.0
:: Description: Complete automation of installation and configuration
:: ============================================================================

color 0A
echo.
echo ================================================================
echo          AI VISION OVERLAY - AUTOMATIC BUILD
echo                  Enterprise-Grade - Modular
echo ================================================================
echo.

:: ============================================================================
:: STEP 1: Check Python environment
:: ============================================================================
echo [1/9] Checking Python environment...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed!
    echo.
    echo Download Python 3.10+ from: https://www.python.org/downloads/
    echo Make sure to add Python to PATH during installation.
    pause
    exit /b 1
)

for /f "tokens=2" %%a in ('python --version') do set PYTHON_VERSION=%%a
echo [OK] Python %PYTHON_VERSION% found
echo.

:: Check Python version (requires 3.10-3.13)
python -c "import sys; exit(0 if (3, 10) <= sys.version_info < (3, 14) else 1)" >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python 3.10-3.13 required!
    echo    Current version: %PYTHON_VERSION%
    echo.
    echo Python 3.14+ is too new - many ML packages don't support it yet.
    echo Please install Python 3.11 or 3.12 from: https://www.python.org/downloads/
    pause
    exit /b 1
)

:: ============================================================================
:: STEP 2: Check pip
:: ============================================================================
echo [2/9] Checking pip...
python -m pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] pip not found, installing...
    python -m ensurepip --default-pip
    python -m pip install --upgrade pip
) else (
    echo [OK] pip installed
    echo.
    echo [UPDATE] Updating pip...
    python -m pip install --upgrade pip --quiet
)
echo.

:: ============================================================================
:: STEP 3: Create virtual environment
:: ============================================================================
echo [3/9] Creating virtual environment...
if exist "venv" (
    echo [WARNING] Virtual environment already exists
    choice /C YN /M "Delete and recreate"
    if !errorlevel! equ 1 (
        echo Removing old environment...
        rmdir /s /q venv
        python -m venv venv
        echo [OK] New environment created
    ) else (
        echo [INFO] Using existing environment
    )
) else (
    python -m venv venv
    echo [OK] Virtual environment created
)
echo.

:: ============================================================================
:: STEP 4: Activate environment
:: ============================================================================
echo [4/9] Activating virtual environment...
call venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo [ERROR] Cannot activate environment
    pause
    exit /b 1
)
echo [OK] Environment active
echo.

:: ============================================================================
:: STEP 5: Install basic tools
:: ============================================================================
echo [5/9] Installing basic tools...
echo.
echo   Installing setuptools, wheel...
python -m pip install --upgrade setuptools wheel --quiet
if %errorlevel% neq 0 (
    echo [ERROR] Error installing tools
    pause
    exit /b 1
)
echo [OK] Tools installed
echo.

:: ============================================================================
:: STEP 6: Install project dependencies
:: ============================================================================
echo [6/9] Installing project dependencies...
echo.
echo   This may take a few minutes...
echo.

if exist "requirements.txt" (
    echo   [FILE] Installing from requirements.txt...
    python -m pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo [WARNING] Issues with some packages
        echo    Continuing installation...
    )
) else (
    echo [WARNING] requirements.txt not found
)

echo.
echo   [PROJECT] Installing in development mode...
python -m pip install -e .
if %errorlevel% neq 0 (
    echo [ERROR] Error installing project
    pause
    exit /b 1
)

echo [OK] Basic dependencies installed
echo.

:: ============================================================================
:: STEP 6.5: GPU Detection and Installation
:: ============================================================================
echo [6.5/9] Detecting and configuring GPU...
echo.

echo   Checking available GPU...
python -c "from src.utils.gpu_detector import GPUDetector; d = GPUDetector(); dtype, backend, info = d.detect(); print(f'DEVICE:{dtype}'); print(f'BACKEND:{backend}'); print(f'NAME:{info.get(\"name\", \"Unknown\")}' if info else 'NAME:CPU')" >gpu_detect.tmp 2>&1

if exist "gpu_detect.tmp" (
    for /f "tokens=2 delims=:" %%a in ('findstr "DEVICE:" gpu_detect.tmp') do set GPU_DEVICE=%%a
    for /f "tokens=2 delims=:" %%a in ('findstr "BACKEND:" gpu_detect.tmp') do set GPU_BACKEND=%%a
    for /f "tokens=2 delims=:" %%a in ('findstr "NAME:" gpu_detect.tmp') do set GPU_NAME=%%a
    del gpu_detect.tmp
)

if not defined GPU_DEVICE set GPU_DEVICE=cpu
if not defined GPU_BACKEND set GPU_BACKEND=cpu
if not defined GPU_NAME set GPU_NAME=CPU

echo.
echo   ====================================================
echo   GPU detected: !GPU_NAME!
echo   Type: !GPU_DEVICE! / Backend: !GPU_BACKEND!
echo   ====================================================
echo.

:: Install appropriate packages for GPU
if "!GPU_DEVICE!"=="cuda" (
    echo   [NVIDIA] NVIDIA GPU detected - installing CUDA support...
    python -m pip uninstall -y torch torchvision
    python -m pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121 --quiet
    if !errorlevel! equ 0 (
        echo   [OK] PyTorch with CUDA installed
    ) else (
        echo   [WARNING] CUDA installation error - using default PyTorch
    )
) else if "!GPU_BACKEND!"=="directml" (
    echo   [AMD] AMD GPU detected on Windows - installing DirectML support...
    python -m pip install torch-directml --quiet
    if !errorlevel! equ 0 (
        echo   [OK] torch-directml installed for AMD GPU
    ) else (
        echo   [WARNING] DirectML installation error - check manually
    )
) else if "!GPU_BACKEND!"=="rocm" (
    echo   [AMD] AMD GPU detected on Linux - installing ROCm support...
    python -m pip uninstall -y torch torchvision
    python -m pip install torch torchvision --index-url https://download.pytorch.org/whl/rocm5.7 --quiet
    if !errorlevel! equ 0 (
        echo   [OK] PyTorch with ROCm installed
    ) else (
        echo   [WARNING] ROCm installation error - using default PyTorch
    )
) else (
    echo   [INFO] Using CPU - application will be slower
    echo   [TIP] If you have GPU, install appropriate drivers:
    echo      - NVIDIA: https://pytorch.org/get-started/locally/
    echo      - AMD Windows: pip install torch-directml
    echo      - AMD Linux: https://pytorch.org/get-started/locally/
)

echo.
echo [OK] GPU configuration complete
echo.

:: ============================================================================
:: STEP 7: Download AI models (optional)
:: ============================================================================
echo [7/9] Configuring AI models...
echo.

if not exist "models" mkdir models

echo   Downloading YOLOv8n model...
python -c "from ultralytics import YOLO; model = YOLO('yolov8n.pt')" >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] YOLOv8n model ready
) else (
    echo [WARNING] Model will be downloaded on first run
)
echo.

:: ============================================================================
:: STEP 8: GPU Test
:: ============================================================================
echo [8/9] Testing GPU configuration...
echo.

echo   Testing GPU...
python -m src.utils.gpu_detector 2>nul
if !errorlevel! equ 0 (
    echo [OK] GPU properly configured
) else (
    echo [WARNING] GPU test failed - check configuration
)
echo.

:: ============================================================================
:: STEP 9: Installation verification
:: ============================================================================
echo [9/9] Verifying installation...
echo.

echo   Checking imports...
python -c "import numpy; import cv2; import yaml" >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Basic libraries not installed properly
    pause
    exit /b 1
)

python -c "import src.core.types; import src.core.config" >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Project modules not installed properly
    pause
    exit /b 1
)

echo [OK] All modules installed successfully
echo.

:: ============================================================================
:: RUN TESTS (optional)
:: ============================================================================
echo.
choice /C YN /M "Run unit tests"
if !errorlevel! equ 1 (
    echo.
    echo [TESTS] Running tests...
    python -m pytest tests/ -v --tb=short
    if !errorlevel! equ 0 (
        echo [OK] All tests passed successfully
    ) else (
        echo [WARNING] Some tests failed
        echo    Application should work, but check logs
    )
)

:: ============================================================================
:: SUMMARY
:: ============================================================================
echo.
echo ================================================================
echo                    BUILD COMPLETED!
echo ================================================================
echo.
echo [SUCCESS] AI Vision Overlay system successfully built!
echo.
echo [STRUCTURE] Project structure:
echo    +- src/          - Source code
echo    +- profiles/     - Game profiles
echo    +- models/       - AI models
echo    +- docs/         - Documentation
echo    +- tests/        - Tests
echo.
echo [RUN] To launch application:
echo    - Run: run.bat
echo    - Or: python -m core.main
echo.
echo [DOCS] Documentation: docs\README_PL.md
echo [EXAMPLES] Example profiles: profiles\darksouls3.yaml
echo.
echo [NEXT STEPS]
echo    1. Check profiles in profiles/ folder
echo    2. Adjust configuration for your game
echo    3. Run application: run.bat
echo.

choice /C YN /M "Launch application now"
if !errorlevel! equ 1 (
    echo.
    echo [LAUNCH] Starting AI Vision Overlay...
    call run.bat
) else (
    echo.
    echo You can run the application later with: run.bat
)

echo.
echo Press any key to exit...
pause >nul

endlocal
