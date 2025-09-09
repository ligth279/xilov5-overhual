"""
Intel GPU utilities for XPU acceleration
Optimized for Intel GPUs with XMX engines (Battlemage architecture)
"""

import torch
import intel_extension_for_pytorch as ipex
import logging
from config import Config

logger = logging.getLogger(__name__)

class IntelGPUManager:
    def __init__(self):
        self.device = None
        self.is_available = False
        self.setup_intel_gpu()
    
    def setup_intel_gpu(self):
        """Initialize Intel GPU for XPU acceleration"""
        try:
            # Check if Intel XPU is available
            if hasattr(torch, 'xpu') and torch.xpu.is_available():
                self.device = torch.device(Config.XPU_DEVICE)
                self.is_available = True
                
                # Get GPU info
                gpu_count = torch.xpu.device_count()
                current_device = torch.xpu.current_device()
                gpu_name = torch.xpu.get_device_name(current_device)
                
                logger.info(f"Intel GPU detected: {gpu_name}")
                logger.info(f"Available XPU devices: {gpu_count}")
                logger.info(f"Using device: {self.device}")
                
                # Set memory fraction to avoid OOM
                if hasattr(torch.xpu, 'set_memory_fraction'):
                    torch.xpu.set_memory_fraction(Config.MEMORY_FRACTION)
                    logger.info(f"Set GPU memory fraction to {Config.MEMORY_FRACTION}")
                
                # Enable optimizations
                torch.xpu.empty_cache()
                logger.info("Intel XPU acceleration enabled!")
                
            else:
                logger.warning("Intel XPU not available, falling back to CPU")
                self.device = torch.device("cpu")
                self.is_available = False
                
        except Exception as e:
            logger.error(f"Error setting up Intel GPU: {e}")
            self.device = torch.device("cpu")
            self.is_available = False
    
    def get_device(self):
        """Get the device to use for model inference"""
        return self.device
    
    def get_device_info(self):
        """Get detailed device information"""
        if not self.is_available:
            return {"device": "cpu", "type": "CPU", "available": False}
        
        try:
            current_device = torch.xpu.current_device()
            gpu_name = torch.xpu.get_device_name(current_device)
            memory_allocated = torch.xpu.memory_allocated(current_device)
            memory_cached = torch.xpu.memory_reserved(current_device)
            
            return {
                "device": str(self.device),
                "type": "Intel XPU",
                "name": gpu_name,
                "available": True,
                "memory_allocated": f"{memory_allocated / 1024**3:.2f} GB",
                "memory_cached": f"{memory_cached / 1024**3:.2f} GB"
            }
        except Exception as e:
            logger.error(f"Error getting device info: {e}")
            return {"device": str(self.device), "type": "Intel XPU", "available": True, "error": str(e)}
    
    def optimize_model(self, model):
        """Apply Intel GPU optimizations to the model"""
        if not self.is_available:
            logger.warning("Intel XPU not available, skipping optimization")
            return model
        
        try:
            # Move model to XPU device
            model = model.to(self.device)
            
            # Apply Intel Extension for PyTorch optimizations
            model = ipex.optimize(model, dtype=torch.float16)
            
            logger.info("Model optimized for Intel XPU")
            return model
            
        except Exception as e:
            logger.error(f"Error optimizing model for Intel GPU: {e}")
            return model
    
    def clear_memory(self):
        """Clear GPU memory cache"""
        if self.is_available:
            try:
                torch.xpu.empty_cache()
                logger.info("Intel XPU memory cache cleared")
            except Exception as e:
                logger.error(f"Error clearing XPU memory: {e}")

# Global instance
gpu_manager = IntelGPUManager()
