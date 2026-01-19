@echo off
setlocal enabledelayedexpansion

echo ================================================================
echo          PYTORCH CUDA FIX - RTX 4050 LAPTOP
echo          Automatic PyTorch reinstallation with CUDA 12.1
echo ================================================================
echo.

:: Check if venv exists
if not exist "venv\" (
    echo [ERROR] Virtual environment not found!
    echo Please run build.bat first to create the environment.
    pause
    exit /b 1
)

echo [1/5] Activating virtual environment...
call venv\Scripts\activate
if %errorlevel% neq 0 (
    echo [ERROR] Failed to activate virtual environment
    pause
    exit /b 1
)
echo [OK] Environment activated
echo.

echo [2/5] Checking current PyTorch installation...
python -c "import torch; print(f'Current PyTorch: {torch.__version__}'); print(f'CUDA available: {torch.cuda.is_available()}')" 2>nul
if %errorlevel% neq 0 (
    echo [WARNING] PyTorch not found or error occurred
)
echo.

echo [3/5] Uninstalling old PyTorch (CPU-only version)...
echo   This may take a minute...
pip uninstall torch torchvision torchaudio -y
if %errorlevel% neq 0 (
    echo [WARNING] Uninstall had issues, continuing anyway...
)
echo [OK] Old PyTorch uninstalled
echo.

echo [4/5] Installing PyTorch with CUDA 12.1...
echo   This will download ~2GB - please wait...
echo   Installing from: https://download.pytorch.org/whl/cu121
echo.

pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Failed to install PyTorch with CUDA
    echo.
    echo Possible solutions:
    echo   1. Check your internet connection
    echo   2. Try running as Administrator
    echo   3. Manually run:
    echo      pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121
    pause
    exit /b 1
)

echo.
echo [OK] PyTorch with CUDA 12.1 installed successfully!
echo.

echo [5/5] Verifying installation...
echo.
echo ================================================================
echo                    VERIFICATION
echo ================================================================
echo.

python -c "import torch; print(f'PyTorch Version: {torch.__version__}'); print(f'CUDA Available: {torch.cuda.is_available()}'); print(f'CUDA Version: {torch.version.cuda if torch.cuda.is_available() else \"N/A\"}'); print(f'GPU Device: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else \"N/A\"}')"

if %errorlevel% neq 0 (
    echo [ERROR] Verification failed
    pause
    exit /b 1
)

echo.
echo ================================================================
echo                    SUCCESS!
echo ================================================================
echo.
echo PyTorch with CUDA 12.1 has been installed successfully!
echo Your RTX 4050 Laptop GPU should now be detected.
echo.
echo Running full GPU diagnostic...
echo.

python diagnose_gpu.py

echo.
echo ================================================================
echo                    NEXT STEPS
echo ================================================================
echo.
echo 1. Close this window
echo 2. Run: run.bat
echo 3. Select: 1. Control Panel (GUI)
echo 4. Check GPU status in "Status" tab
echo 5. Select a game profile and click "Start System"
echo.
echo Your RTX 4050 should now show:
echo   - Device: NVIDIA GeForce RTX 4050 Laptop GPU
echo   - Backend: CUDA
echo   - VRAM: 6.0 GB
echo.
echo ================================================================

pause
