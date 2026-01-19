"""
Wykrywanie i konfiguracja GPU dla AI Vision.
Wspiera: NVIDIA CUDA, AMD ROCm/DirectML, Intel.
"""

import sys
import subprocess
from pathlib import Path
from typing import Optional, Dict, Tuple
from loguru import logger


class GPUDetector:
    """
    Inteligentna detekcja GPU i konfiguracja dla PyTorch.

    Wspierane platformy:
    - NVIDIA (CUDA) - RTX 4050, RTX 3000/4000 series
    - AMD (ROCm/DirectML) - RX 7900 GRE, RX 6000/7000 series
    - Intel (OpenVINO)
    - CPU fallback
    """

    def __init__(self):
        self.gpu_info: Dict = {}
        self.device_type: str = "cpu"
        self.device_name: str = "CPU"
        self.backend: str = "cpu"

    def detect(self) -> Tuple[str, str, Dict]:
        """
        Wykryj dostępne GPU i wybierz najlepsze.

        Returns:
            Tuple[device_type, backend, gpu_info]
            device_type: "cuda", "rocm", "directml", "cpu"
            backend: nazwa backend'u do użycia
            gpu_info: informacje o GPU
        """
        logger.info("🔍 Wykrywanie dostępnych GPU...")

        # Próba 1: NVIDIA CUDA
        if self._detect_nvidia_cuda():
            return self.device_type, self.backend, self.gpu_info

        # Próba 2: AMD ROCm (Linux)
        if sys.platform == "linux" and self._detect_amd_rocm():
            return self.device_type, self.backend, self.gpu_info

        # Próba 3: AMD DirectML (Windows)
        if sys.platform == "win32" and self._detect_amd_directml():
            return self.device_type, self.backend, self.gpu_info

        # Próba 4: Intel OpenVINO
        if self._detect_intel():
            return self.device_type, self.backend, self.gpu_info

        # Fallback: CPU
        logger.warning("⚠️  Nie wykryto GPU - używam CPU")
        self.device_type = "cpu"
        self.backend = "cpu"
        self.device_name = "CPU"
        return self.device_type, self.backend, self.gpu_info

    def _detect_nvidia_cuda(self) -> bool:
        """Wykryj NVIDIA GPU z CUDA."""
        # First, check if NVIDIA GPU exists in system (Windows)
        nvidia_gpu_name = None
        if sys.platform == "win32":
            try:
                # Try to find wmic.exe
                import shutil
                wmic_path = shutil.which("wmic")
                if not wmic_path:
                    # Try common system paths
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

                    # Find NVIDIA GPU
                    for name in gpu_names:
                        if "NVIDIA" in name or "GeForce" in name or "RTX" in name:
                            nvidia_gpu_name = name
                            logger.info(f"🔍 System detected NVIDIA GPU: {name}")
                            break
                else:
                    logger.debug("WMIC not found in system")
            except Exception as e:
                logger.debug(f"WMIC detection failed: {e}")

        # Try PyTorch CUDA detection
        try:
            import torch
            if torch.cuda.is_available():
                device_count = torch.cuda.device_count()
                device_name = torch.cuda.get_device_name(0)
                cuda_version = torch.version.cuda

                self.device_type = "cuda"
                self.backend = "cuda"
                self.device_name = device_name
                self.gpu_info = {
                    "vendor": "NVIDIA",
                    "name": device_name,
                    "count": device_count,
                    "cuda_version": cuda_version,
                    "compute_capability": torch.cuda.get_device_capability(0),
                    "memory_total_gb": torch.cuda.get_device_properties(0).total_memory / (1024**3),
                }

                logger.info(f"✅ Wykryto NVIDIA GPU: {device_name}")
                logger.info(f"   CUDA: {cuda_version}")
                logger.info(f"   Pamięć: {self.gpu_info['memory_total_gb']:.1f} GB")

                # Specjalna optymalizacja dla RTX 4050 (laptop)
                if "4050" in device_name or "RTX 40" in device_name:
                    logger.info("🎯 Wykryto RTX 4050 - włączam optymalizacje dla laptop GPU")
                    self.gpu_info["laptop_mode"] = True
                    self.gpu_info["tensor_cores"] = True
                    self.gpu_info["recommended_batch_size"] = 2

                return True
            elif nvidia_gpu_name:
                # PyTorch doesn't see CUDA, but NVIDIA GPU exists
                logger.warning(f"⚠️  NVIDIA GPU detected ({nvidia_gpu_name}) but PyTorch CUDA unavailable!")
                logger.warning("   Install PyTorch with CUDA support:")
                logger.warning("   pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121")

                # Still mark as detected for UI purposes
                self.device_type = "cuda"
                self.backend = "cuda_unavailable"
                self.device_name = nvidia_gpu_name
                self.gpu_info = {
                    "vendor": "NVIDIA",
                    "name": nvidia_gpu_name,
                    "status": "CUDA not configured",
                    "needs_install": True
                }

                return True

        except ImportError:
            if nvidia_gpu_name:
                logger.warning(f"⚠️  NVIDIA GPU detected ({nvidia_gpu_name}) but PyTorch not installed!")
                logger.warning("   Install PyTorch with CUDA support:")
                logger.warning("   pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121")

                self.device_type = "cuda"
                self.backend = "pytorch_missing"
                self.device_name = nvidia_gpu_name
                self.gpu_info = {
                    "vendor": "NVIDIA",
                    "name": nvidia_gpu_name,
                    "status": "PyTorch not installed",
                    "needs_install": True
                }
                return True
            logger.debug("PyTorch z CUDA nie zainstalowany")
        except Exception as e:
            logger.debug(f"Błąd detekcji CUDA: {e}")

        return False

    def _detect_amd_rocm(self) -> bool:
        """Wykryj AMD GPU z ROCm (Linux)."""
        try:
            import torch
            if hasattr(torch, 'hip') and torch.hip.is_available():
                device_name = torch.hip.get_device_name(0)
                rocm_version = torch.version.hip

                self.device_type = "rocm"
                self.backend = "rocm"
                self.device_name = device_name
                self.gpu_info = {
                    "vendor": "AMD",
                    "name": device_name,
                    "rocm_version": rocm_version,
                }

                logger.info(f"✅ Wykryto AMD GPU (ROCm): {device_name}")
                logger.info(f"   ROCm: {rocm_version}")

                # Specjalna optymalizacja dla RX 7900 GRE
                if "7900" in device_name or "RX 7900" in device_name:
                    logger.info("🎯 Wykryto RX 7900 GRE - włączam optymalizacje dla high-end AMD")
                    self.gpu_info["high_end"] = True
                    self.gpu_info["recommended_batch_size"] = 4

                return True

        except ImportError:
            logger.debug("PyTorch z ROCm nie zainstalowany")
        except Exception as e:
            logger.debug(f"Błąd detekcji ROCm: {e}")

        return False

    def _detect_amd_directml(self) -> bool:
        """Wykryj AMD GPU z DirectML (Windows)."""
        try:
            # Sprawdź czy DirectML jest dostępny
            import torch_directml

            if torch_directml.is_available():
                device = torch_directml.device()

                # Próba wykrycia nazwy GPU przez wmic (Windows)
                try:
                    result = subprocess.run(
                        ["wmic", "path", "win32_VideoController", "get", "name"],
                        capture_output=True,
                        text=True,
                        timeout=5
                    )
                    gpu_names = [line.strip() for line in result.stdout.split('\n')
                                if line.strip() and 'Name' not in line]

                    # Szukaj AMD GPU
                    amd_gpu = None
                    for name in gpu_names:
                        if "AMD" in name or "Radeon" in name:
                            amd_gpu = name
                            break

                    device_name = amd_gpu or "AMD GPU (DirectML)"

                except Exception:
                    device_name = "AMD GPU (DirectML)"

                self.device_type = "directml"
                self.backend = "directml"
                self.device_name = device_name
                self.gpu_info = {
                    "vendor": "AMD",
                    "name": device_name,
                    "backend": "DirectML",
                }

                logger.info(f"✅ Wykryto AMD GPU (DirectML): {device_name}")

                # Specjalna optymalizacja dla RX 7900 GRE
                if "7900" in device_name:
                    logger.info("🎯 Wykryto RX 7900 GRE - włączam optymalizacje dla high-end AMD")
                    self.gpu_info["high_end"] = True
                    self.gpu_info["recommended_batch_size"] = 4

                return True

        except ImportError:
            logger.debug("torch-directml nie zainstalowany")
        except Exception as e:
            logger.debug(f"Błąd detekcji DirectML: {e}")

        return False

    def _detect_intel(self) -> bool:
        """Wykryj Intel GPU."""
        # TODO: Implementacja Intel OpenVINO
        return False

    def get_optimal_config(self) -> Dict:
        """
        Zwróć optymalną konfigurację dla wykrytego GPU.

        Returns:
            Dict z rekomendowanymi ustawieniami
        """
        config = {
            "device": self.device_type,
            "backend": self.backend,
            "fp16": False,
            "batch_size": 1,
            "num_workers": 2,
            "pin_memory": False,
        }

        if self.device_type == "cuda":
            # NVIDIA CUDA - pełna moc
            config.update({
                "fp16": True if self.gpu_info.get("compute_capability", (0, 0))[0] >= 7 else False,
                "batch_size": self.gpu_info.get("recommended_batch_size", 2),
                "num_workers": 4,
                "pin_memory": True,
                "cudnn_benchmark": True,
            })

            # RTX 4050 - laptop, oszczędzaj energię
            if self.gpu_info.get("laptop_mode"):
                logger.info("💡 Tryb laptop - ograniczam zużycie energii")
                config["batch_size"] = 2
                config["power_limit"] = 0.8  # 80% mocy

        elif self.device_type == "rocm":
            # AMD ROCm
            config.update({
                "fp16": True,
                "batch_size": self.gpu_info.get("recommended_batch_size", 4),
                "num_workers": 4,
                "pin_memory": True,
            })

        elif self.device_type == "directml":
            # AMD DirectML (Windows)
            config.update({
                "fp16": False,  # DirectML ma problemy z fp16
                "batch_size": self.gpu_info.get("recommended_batch_size", 2),
                "num_workers": 2,
                "pin_memory": False,
            })

            # RX 7900 GRE - high-end, można więcej
            if self.gpu_info.get("high_end"):
                config["batch_size"] = 4

        else:
            # CPU fallback
            logger.warning("⚠️  Używam CPU - wydajność będzie ograniczona")
            config.update({
                "batch_size": 1,
                "num_workers": 2,
            })

        return config

    def install_instructions(self) -> str:
        """
        Zwróć instrukcje instalacji dla brakującego wsparcia GPU.

        Returns:
            String z instrukcjami instalacji
        """
        if self.device_type == "cpu":
            return """
╔════════════════════════════════════════════════════════════════╗
║              WSPARCIE GPU - INSTRUKCJE INSTALACJI              ║
╚════════════════════════════════════════════════════════════════╝

🔍 Nie wykryto GPU lub brak wsparcia. Wybierz opcję:

📌 NVIDIA GPU (RTX 4050, RTX 3000/4000 series):
   pip uninstall torch torchvision
   pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121

📌 AMD GPU - Windows (RX 7900 GRE, RX 6000/7000 series):
   pip install torch-directml

📌 AMD GPU - Linux (ROCm):
   pip install torch torchvision --index-url https://download.pytorch.org/whl/rocm5.7

📌 CPU (Fallback):
   Brak dodatkowych kroków - aplikacja będzie działać wolniej

Po instalacji uruchom ponownie: run.bat
"""
        return ""


def get_pytorch_device():
    """
    Pomocnicza funkcja do szybkiego uzyskania urządzenia PyTorch.

    Returns:
        str: "cuda", "cpu", itp.
    """
    detector = GPUDetector()
    device_type, backend, info = detector.detect()

    return device_type


def print_gpu_info():
    """Wyświetl informacje o GPU w konsoli."""
    detector = GPUDetector()
    device_type, backend, info = detector.detect()

    print("\n" + "="*60)
    print("GPU INFORMATION / INFORMACJE O GPU")
    print("="*60)
    print(f"Device Type:    {device_type.upper()}")
    print(f"Backend:        {backend}")
    print(f"GPU Name:       {detector.device_name}")

    if info:
        print(f"Vendor:         {info.get('vendor', 'N/A')}")
        if 'cuda_version' in info:
            print(f"CUDA Version:   {info['cuda_version']}")
        if 'rocm_version' in info:
            print(f"ROCm Version:   {info['rocm_version']}")
        if 'memory_total_gb' in info:
            print(f"Memory:         {info['memory_total_gb']:.1f} GB")

    config = detector.get_optimal_config()
    print("\nOptimal Config:")
    print(f"  Batch Size:   {config['batch_size']}")
    print(f"  FP16:         {config['fp16']}")
    print(f"  Workers:      {config['num_workers']}")
    print("="*60 + "\n")


if __name__ == "__main__":
    # Test detekcji
    print_gpu_info()

    detector = GPUDetector()
    if detector.device_type == "cpu":
        print(detector.install_instructions())
