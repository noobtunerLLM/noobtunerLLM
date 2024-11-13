import torch
import psutil
import os
import subprocess
import sys
from typing import Dict, Optional
from dataclasses import dataclass
from pathlib import Path

from noobTunerLLM.logger import logger
from noobTunerLLM.exception import FineTuningException

@dataclass
class SystemRequirements:
    min_ram_gb: int = 16
    min_gpu_memory_gb: int = 8
    min_cuda_version: str = "11.7"
    min_torch_version: str = "2.0.0"

@dataclass
class SystemStats:
    total_ram_gb: float
    available_ram_gb: float
    gpu_name: Optional[str]
    gpu_memory_gb: Optional[float]
    cuda_version: Optional[str]
    torch_version: str
    gpu_compute_capability: Optional[tuple]

class ConfigurationChecker:
    """
    Utility class to check system configuration for LLM fine-tuning compatibility
    """
    def __init__(self, requirements: Optional[SystemRequirements] = None):
        self.requirements = requirements or SystemRequirements()
        
    def get_system_stats(self) -> SystemStats:
        """Collect system statistics"""
        try:
            # RAM information
            ram = psutil.virtual_memory()
            total_ram_gb = ram.total / (1024 ** 3)
            available_ram_gb = ram.available / (1024 ** 3)
            
            # GPU information
            if torch.cuda.is_available():
                gpu_name = torch.cuda.get_device_name(0)
                gpu_memory_gb = torch.cuda.get_device_properties(0).total_memory / (1024 ** 3)
                cuda_version = torch.version.cuda
                gpu_compute_capability = torch.cuda.get_device_capability()
            else:
                gpu_name = None
                gpu_memory_gb = None
                cuda_version = None
                gpu_compute_capability = None
            
            return SystemStats(
                total_ram_gb=total_ram_gb,
                available_ram_gb=available_ram_gb,
                gpu_name=gpu_name,
                gpu_memory_gb=gpu_memory_gb,
                cuda_version=cuda_version,
                torch_version=torch.__version__,
                gpu_compute_capability=gpu_compute_capability
            )
            
        except Exception as e:
            logger.error(f"Error getting system stats: {str(e)}")
            raise FineTuningException(e, sys)
    
    def check_flash_attention_compatibility(self) -> Dict:
        """Check if the system can use Flash Attention"""
        try:
            stats = self.get_system_stats()
            
            if not stats.gpu_compute_capability:
                return {
                    "status": "noob",
                    "message": "No GPU detected. Flash Attention requires NVIDIA GPU.",
                    "can_use_flash_attn": False,
                    "attn_implementation": "eager"
                }
            
            major_version = stats.gpu_compute_capability[0]
            
            if major_version >= 8:
                return {
                    "status": "pro",
                    "message": f"GPU {stats.gpu_name} supports Flash Attention 2.0",
                    "can_use_flash_attn": True,
                    "attn_implementation": "flash_attention_2"
                }
            else:
                return {
                    "status": "noob",
                    "message": f"GPU {stats.gpu_name} does not meet minimum requirements for Flash Attention",
                    "can_use_flash_attn": False,
                    "attn_implementation": "eager"
                }
                
        except Exception as e:
            logger.error(f"Error checking Flash Attention compatibility: {str(e)}")
            raise FineTuningException(e, sys)
    
    def check_system_compatibility(self) -> Dict:
        """Comprehensive system compatibility check"""
        try:
            stats = self.get_system_stats()
            flash_attn_info = self.check_flash_attention_compatibility()
            
            checks = {
                "ram": stats.total_ram_gb >= self.requirements.min_ram_gb,
                "gpu": stats.gpu_name is not None,
                "gpu_memory": (stats.gpu_memory_gb or 0) >= self.requirements.min_gpu_memory_gb,
                "cuda": stats.cuda_version is not None,
                "torch": stats.torch_version >= self.requirements.min_torch_version
            }
            
            status = "pro" if all(checks.values()) else "noob"
            missing_requirements = [req for req, check in checks.items() if not check]
            
            return {
                "status": status,
                "system_stats": stats,
                "checks": checks,
                "missing_requirements": missing_requirements,
                "flash_attention": flash_attn_info,
                "can_proceed": bool(stats.gpu_name)  # Basic requirement to proceed
            }
            
        except Exception as e:
            logger.error(f"Error checking system compatibility: {str(e)}")
            raise FineTuningException(e, sys)
    
    @staticmethod
    def install_flash_attention() -> bool:
        """Install Flash Attention package"""
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "flash-attn"])
            return True
        except Exception as e:
            logger.error(f"Error installing Flash Attention: {str(e)}")
            return False

    def get_recommended_batch_size(self) -> int:
        """Calculate recommended batch size based on available GPU memory"""
        try:
            stats = self.get_system_stats()
            if not stats.gpu_memory_gb:
                return 1
                
            # Conservative estimate - adjust these values based on your model
            memory_per_sample_gb = 0.5
            system_overhead_gb = 2
            
            available_memory = stats.gpu_memory_gb - system_overhead_gb
            recommended_batch_size = max(1, int(available_memory / memory_per_sample_gb))
            
            return min(recommended_batch_size, 32)  # Cap at 32
            
        except Exception as e:
            logger.error(f"Error calculating recommended batch size: {str(e)}")
            return 1