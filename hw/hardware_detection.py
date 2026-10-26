#!/usr/bin/env python3
"""
Hardware Detection & Optimization
Detects hardware capabilities and optimizes processing.
"""

import platform
import subprocess
from typing import Dict, Optional, Tuple
from enum import Enum
from loguru import logger

try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False


class ComputeDevice(Enum):
    """Available compute devices"""
    CPU = "cpu"
    CUDA = "cuda"
    METAL = "mps"  # Apple Metal Performance Shaders
    OPENCL = "opencl"


class HardwareProfile:
    """System hardware profile"""

    def __init__(
        self,
        device: ComputeDevice,
        gpu_name: Optional[str] = None,
        vram_gb: float = 0.0,
        cpu_cores: int = 1,
        ram_gb: float = 0.0
    ):
        self.device = device
        self.gpu_name = gpu_name
        self.vram_gb = vram_gb
        self.cpu_cores = cpu_cores
        self.ram_gb = ram_gb


class HardwareDetector:
    """Detects and profiles system hardware"""

    def __init__(self):
        """
        Initialize HardwareDetector
        """
        logger.info("HardwareDetector initialized")

    def detect_hardware(self) -> HardwareProfile:
        """
        Detect available hardware
        
        Returns:
            HardwareProfile object
        """
        logger.info("Detecting hardware...")
        
        # Detect CPU info
        cpu_cores = self._detect_cpu_cores()
        ram_gb = self._detect_ram()
        
        # Detect GPU
        device, gpu_name, vram_gb = self._detect_gpu()
        
        profile = HardwareProfile(
            device=device,
            gpu_name=gpu_name,
            vram_gb=vram_gb,
            cpu_cores=cpu_cores,
            ram_gb=ram_gb
        )
        
        self._log_profile(profile)
        return profile

    def _detect_cpu_cores(self) -> int:
        """
        Detect number of CPU cores
        
        Returns:
            Number of cores
        """
        try:
            import os
            return os.cpu_count() or 1
        except Exception as e:
            logger.warning(f"Could not detect CPU cores: {e}")
            return 1

    def _detect_ram(self) -> float:
        """
        Detect available RAM
        
        Returns:
            RAM in GB
        """
        try:
            import psutil
            return psutil.virtual_memory().total / (1024 ** 3)
        except ImportError:
            logger.debug("psutil not available, skipping RAM detection")
            return 0.0
        except Exception as e:
            logger.warning(f"Could not detect RAM: {e}")
            return 0.0

    def _detect_gpu(self) -> Tuple[ComputeDevice, Optional[str], float]:
        """
        Detect available GPU
        
        Returns:
            Tuple of (device, gpu_name, vram_gb)
        """
        # Try NVIDIA CUDA
        if TORCH_AVAILABLE and torch.cuda.is_available():
            try:
                device_count = torch.cuda.device_count()
                if device_count > 0:
                    gpu_name = torch.cuda.get_device_name(0)
                    vram_bytes = torch.cuda.get_device_properties(0).total_memory
                    vram_gb = vram_bytes / (1024 ** 3)
                    logger.success(f"NVIDIA GPU detected: {gpu_name} ({vram_gb:.2f}GB VRAM)")
                    return ComputeDevice.CUDA, gpu_name, vram_gb
            except Exception as e:
                logger.debug(f"CUDA detection failed: {e}")
        
        # Try Apple Metal
        if platform.system() == "Darwin":
            try:
                if TORCH_AVAILABLE and hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
                    logger.success("Apple Metal GPU detected")
                    return ComputeDevice.METAL, "Apple Metal Performance Shaders", 0.0
            except Exception as e:
                logger.debug(f"Metal detection failed: {e}")
        
        # Try AMD OpenCL
        if self._detect_amd_gpu():
            logger.success("AMD GPU detected")
            return ComputeDevice.OPENCL, "AMD GPU (OpenCL)", 0.0
        
        # Fallback to CPU
        logger.info("No GPU detected, using CPU")
        return ComputeDevice.CPU, None, 0.0

    def _detect_amd_gpu(self) -> bool:
        """
        Detect AMD GPU
        
        Returns:
            True if AMD GPU found
        """
        try:
            if platform.system() == "Linux":
                result = subprocess.run(['rocm-smi'], capture_output=True, timeout=5)
                return result.returncode == 0
        except Exception:
            pass
        return False

    def _log_profile(self, profile: HardwareProfile) -> None:
        """
        Log hardware profile
        
        Args:
            profile: HardwareProfile object
        """
        logger.success(f"Hardware Profile:")
        logger.success(f"  Device: {profile.device.value}")
        if profile.gpu_name:
            logger.success(f"  GPU: {profile.gpu_name} ({profile.vram_gb:.2f}GB VRAM)")
        logger.success(f"  CPU Cores: {profile.cpu_cores}")
        logger.success(f"  RAM: {profile.ram_gb:.2f}GB")


class HardwareOptimizer:
    """Optimizes processing based on hardware"""

    def __init__(self, profile: HardwareProfile):
        """
        Initialize HardwareOptimizer
        
        Args:
            profile: HardwareProfile object
        """
        self.profile = profile
        logger.info(f"HardwareOptimizer configured for {profile.device.value}")

    def get_optimal_settings(self) -> Dict:
        """
        Get optimal processing settings
        
        Returns:
            Settings dictionary
        """
        if self.profile.device == ComputeDevice.CUDA:
            return self._get_cuda_settings()
        elif self.profile.device == ComputeDevice.METAL:
            return self._get_metal_settings()
        elif self.profile.device == ComputeDevice.OPENCL:
            return self._get_opencl_settings()
        else:
            return self._get_cpu_settings()

    def _get_cuda_settings(self) -> Dict:
        """
        Get optimal CUDA settings
        
        Returns:
            Settings dictionary
        """
        if self.profile.vram_gb >= 8:
            batch_size = 32
            frame_resolution = 1080
        elif self.profile.vram_gb >= 4:
            batch_size = 16
            frame_resolution = 720
        else:
            batch_size = 8
            frame_resolution = 480
        
        return {
            'device': 'cuda',
            'batch_size': batch_size,
            'frame_resolution': frame_resolution,
            'num_workers': min(self.profile.cpu_cores, 8),
            'precision': 'fp32' if self.profile.vram_gb < 4 else 'fp32'
        }

    def _get_metal_settings(self) -> Dict:
        """
        Get optimal Apple Metal settings
        
        Returns:
            Settings dictionary
        """
        return {
            'device': 'mps',
            'batch_size': 8,
            'frame_resolution': 720,
            'num_workers': 4,
            'precision': 'fp32'
        }

    def _get_opencl_settings(self) -> Dict:
        """
        Get optimal OpenCL settings
        
        Returns:
            Settings dictionary
        """
        return {
            'device': 'opencl',
            'batch_size': 8,
            'frame_resolution': 480,
            'num_workers': 4,
            'precision': 'fp32'
        }

    def _get_cpu_settings(self) -> Dict:
        """
        Get optimal CPU settings
        
        Returns:
            Settings dictionary
        """
        resolution = 1080 if self.profile.ram_gb >= 16 else 720 if self.profile.ram_gb >= 8 else 480
        
        return {
            'device': 'cpu',
            'batch_size': 1,
            'frame_resolution': resolution,
            'num_workers': 1,
            'precision': 'fp32',
            'enable_mmap': True  # Memory mapping for large files
        }
