"""
GPU resource manager for tracking GPU availability and health.
"""
from typing import Dict, List, Optional
import time

try:
    import pynvml
    PYNVML_AVAILABLE = True
except ImportError:
    PYNVML_AVAILABLE = False

from observability.logging import get_logger
from app.core.config import settings

logger = get_logger(__name__)


class GPUManager:
    """Manages GPU resources and availability."""
    
    def __init__(self):
        """Initialize GPU manager."""
        self.gpus: Dict[int, Dict[str, any]] = {}
        self.initialized = False
        
        if PYNVML_AVAILABLE:
            try:
                pynvml.nvmlInit()
                self.initialized = True
                self._discover_gpus()
                logger.info(f"GPU Manager initialized: {len(self.gpus)} GPUs found")
            except Exception as e:
                logger.warning(f"Failed to initialize NVML: {e}")
        else:
            logger.warning("pynvml not available, GPU monitoring disabled")
    
    def _discover_gpus(self):
        """Discover available GPUs."""
        if not self.initialized:
            return
        
        try:
            device_count = pynvml.nvmlDeviceGetCount()
            for i in range(device_count):
                handle = pynvml.nvmlDeviceGetHandleByIndex(i)
                name = pynvml.nvmlDeviceGetName(handle).decode('utf-8')
                
                self.gpus[i] = {
                    "id": i,
                    "name": name,
                    "handle": handle,
                    "available": True,
                    "memory_total": 0,
                    "memory_used": 0,
                    "memory_free": 0,
                    "utilization": 0,
                    "temperature": 0,
                    "last_update": time.time(),
                }
                self._update_gpu_info(i)
            
            logger.info(f"Discovered {len(self.gpus)} GPUs")
        except Exception as e:
            logger.error(f"Error discovering GPUs: {e}")
    
    def _update_gpu_info(self, gpu_id: int):
        """Update GPU information."""
        if not self.initialized or gpu_id not in self.gpus:
            return
        
        try:
            gpu = self.gpus[gpu_id]
            handle = gpu["handle"]
            
            # Memory info
            mem_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
            gpu["memory_total"] = mem_info.total
            gpu["memory_used"] = mem_info.used
            gpu["memory_free"] = mem_info.free
            
            # Utilization
            util = pynvml.nvmlDeviceGetUtilizationRates(handle)
            gpu["utilization"] = util.gpu
            
            # Temperature
            try:
                temp = pynvml.nvmlDeviceGetTemperature(handle, pynvml.NVML_TEMPERATURE_GPU)
                gpu["temperature"] = temp
            except:
                pass
            
            gpu["last_update"] = time.time()
            
        except Exception as e:
            logger.error(f"Error updating GPU {gpu_id} info: {e}")
    
    def get_available_gpu(self, min_memory_gb: float = 2.0) -> Optional[int]:
        """
        Get an available GPU with sufficient memory.
        
        Args:
            min_memory_gb: Minimum free memory in GB
            
        Returns:
            GPU ID or None if no GPU available
        """
        self.update_all_gpus()
        
        min_memory_bytes = min_memory_gb * 1024 * 1024 * 1024
        
        for gpu_id, gpu in self.gpus.items():
            if not gpu["available"]:
                continue
            
            if gpu["memory_free"] < min_memory_bytes:
                continue
            
            # Check utilization (prefer less utilized GPUs)
            if gpu["utilization"] > 90:
                continue
            
            return gpu_id
        
        return None
    
    def update_all_gpus(self):
        """Update information for all GPUs."""
        for gpu_id in self.gpus.keys():
            self._update_gpu_info(gpu_id)
    
    def get_gpu_info(self, gpu_id: int) -> Optional[Dict[str, any]]:
        """
        Get GPU information.
        
        Args:
            gpu_id: GPU ID
            
        Returns:
            GPU info dictionary or None if not found
        """
        if gpu_id not in self.gpus:
            return None
        
        self._update_gpu_info(gpu_id)
        return self.gpus[gpu_id].copy()
    
    def get_all_gpus(self) -> List[Dict[str, any]]:
        """
        Get information for all GPUs.
        
        Returns:
            List of GPU info dictionaries
        """
        self.update_all_gpus()
        return [gpu.copy() for gpu in self.gpus.values()]
    
    def mark_gpu_busy(self, gpu_id: int):
        """Mark GPU as busy."""
        if gpu_id in self.gpus:
            self.gpus[gpu_id]["available"] = False
            logger.info(f"GPU {gpu_id} marked as busy")
    
    def mark_gpu_available(self, gpu_id: int):
        """Mark GPU as available."""
        if gpu_id in self.gpus:
            self.gpus[gpu_id]["available"] = True
            logger.info(f"GPU {gpu_id} marked as available")
    
    def __del__(self):
        """Cleanup on destruction."""
        if self.initialized and PYNVML_AVAILABLE:
            try:
                # NVML doesn't have explicit shutdown, but we can log
                logger.debug("GPU Manager shutting down")
            except:
                pass

