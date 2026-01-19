"""
GPU Diagnostic Tool - Check GPU detection and CUDA support
"""

import sys
import subprocess
from pathlib import Path

print("=" * 70)
print("GPU DIAGNOSTIC TOOL")
print("=" * 70)
print()

# 1. Check system GPUs (Windows)
print("[1/6] Checking system GPUs via WMIC...")
if sys.platform == "win32":
    try:
        import shutil
        wmic_path = shutil.which("wmic")

        if not wmic_path:
            possible_paths = [
                r"C:\Windows\System32\wbem\wmic.exe",
                r"C:\Windows\SysWOW64\wbem\wmic.exe"
            ]
            for path in possible_paths:
                if Path(path).exists():
                    wmic_path = path
                    break

        if wmic_path:
            result = subprocess.run(
                [wmic_path, "path", "win32_VideoController", "get", "name"],
                capture_output=True,
                text=True,
                timeout=5,
                creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
            )

            gpu_names = [line.strip() for line in result.stdout.split('\n')
                        if line.strip() and 'Name' not in line]

            print("✅ System GPUs detected:")
            for idx, name in enumerate(gpu_names, 1):
                print(f"   {idx}. {name}")

            # Highlight NVIDIA
            nvidia_gpus = [n for n in gpu_names if "NVIDIA" in n or "GeForce" in n or "RTX" in n]
            if nvidia_gpus:
                print(f"\n🎯 NVIDIA GPU found: {nvidia_gpus[0]}")
            else:
                print("\n⚠️  No NVIDIA GPU detected")
        else:
            print("❌ WMIC not found")
    except Exception as e:
        print(f"❌ Error: {e}")
else:
    print("⚠️  WMIC check only available on Windows")

print()

# 2. Check PyTorch installation
print("[2/6] Checking PyTorch installation...")
try:
    import torch
    print(f"✅ PyTorch installed: {torch.__version__}")
except ImportError:
    print("❌ PyTorch NOT installed")
    print("   Install: pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121")
    sys.exit(1)

print()

# 3. Check CUDA availability
print("[3/6] Checking CUDA availability...")
try:
    import torch

    cuda_available = torch.cuda.is_available()
    print(f"CUDA Available: {cuda_available}")

    if cuda_available:
        print(f"✅ CUDA Version: {torch.version.cuda}")
        print(f"✅ cuDNN Version: {torch.backends.cudnn.version()}")
        print(f"✅ GPU Count: {torch.cuda.device_count()}")

        for i in range(torch.cuda.device_count()):
            print(f"\n   GPU {i}:")
            print(f"   - Name: {torch.cuda.get_device_name(i)}")
            props = torch.cuda.get_device_properties(i)
            print(f"   - Memory: {props.total_memory / (1024**3):.1f} GB")
            print(f"   - Compute Capability: {props.major}.{props.minor}")
    else:
        print("❌ CUDA NOT available")
        print("\n   PyTorch is installed without CUDA support (CPU-only)")
        print("   This is the most likely issue!")
        print("\n   To fix:")
        print("   1. Uninstall current PyTorch:")
        print("      pip uninstall torch torchvision torchaudio")
        print("   2. Install PyTorch with CUDA 12.1:")
        print("      pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121")

except Exception as e:
    print(f"❌ Error checking CUDA: {e}")

print()

# 4. Check torch build info
print("[4/6] Checking PyTorch build configuration...")
try:
    import torch
    print(f"PyTorch built with CUDA: {torch.cuda.is_available()}")
    print(f"PyTorch version: {torch.__version__}")
    print(f"Is CUDA build: {'Yes' if '+cu' in torch.__version__ else 'No (CPU-only!)'}")

    if '+cu' in torch.__version__:
        print(f"✅ CUDA version in build: {torch.__version__.split('+')[1]}")
    else:
        print("❌ This is a CPU-only PyTorch build")
        print("   You need to reinstall PyTorch with CUDA support")
except Exception as e:
    print(f"Error: {e}")

print()

# 5. Check NVIDIA drivers
print("[5/6] Checking NVIDIA drivers...")
try:
    result = subprocess.run(
        ["nvidia-smi"],
        capture_output=True,
        text=True,
        timeout=5
    )

    if result.returncode == 0:
        print("✅ NVIDIA drivers installed")
        print("\nnvidia-smi output:")
        print("-" * 70)
        print(result.stdout[:500])  # First 500 chars
    else:
        print("❌ nvidia-smi failed")
except FileNotFoundError:
    print("❌ nvidia-smi not found")
    print("   Install NVIDIA drivers from: https://www.nvidia.com/Download/index.aspx")
except Exception as e:
    print(f"Error: {e}")

print()

# 6. Summary and recommendations
print("[6/6] Summary and Recommendations")
print("=" * 70)

try:
    import torch

    if torch.cuda.is_available():
        print("✅ ALL GOOD! GPU is properly configured")
        print(f"   GPU: {torch.cuda.get_device_name(0)}")
        print(f"   CUDA: {torch.version.cuda}")
    else:
        print("⚠️  ISSUE DETECTED: CUDA not available")
        print("\nMost likely cause:")
        print("   PyTorch was installed WITHOUT CUDA support (CPU-only version)")

        print("\n🔧 SOLUTION:")
        print("   1. Open Command Prompt as Administrator")
        print("   2. Activate your venv:")
        print("      venv\\Scripts\\activate")
        print("   3. Uninstall PyTorch:")
        print("      pip uninstall torch torchvision torchaudio -y")
        print("   4. Install PyTorch with CUDA 12.1:")
        print("      pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121")
        print("   5. Verify:")
        print("      python diagnose_gpu.py")

except ImportError:
    print("❌ PyTorch not installed")
    print("   Install: pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121")

print()
print("=" * 70)
print("Diagnostic complete!")
print("=" * 70)
