"""
Intel GPU utilities for XPU acceleration
Optimized for Intel GPUs with XMX engines (Battlemage architecture)

IMPORTANT: This module must be initialized AFTER ipex-llm loads the model
to avoid IPEX import conflicts. Call post_model_load_setup() after model loads.

CRITICAL: Do NOT import torch at module level! In PyTorch 2.6+xpu, importing torch
auto-loads IPEX, which conflicts with ipex-llm. Import torch locally in methods.
"""

# DO NOT import torch here - it auto-loads IPEX in PyTorch 2.6!
import logging
from config import Config

logger = logging.getLogger(__name__)

class IntelGPUManager:
    def __init__(self):
        self.device = None
        self.is_available = False
        self._initialized = False
        # Do NOT call any torch.xpu methods here - they auto-import IPEX in PyTorch 2.6!
    
    def post_model_load_setup(self):
        """
        Initialize Intel GPU utilities AFTER ipex-llm has loaded the model.
        This must be called after model loading to avoid IPEX import conflicts.
        """
        if self._initialized:
            return
        
        # Import torch HERE - after ipex-llm has already loaded it
        import torch
            
        try:
            # NOW it's safe to check XPU - ipex-llm has already imported IPEX
            if hasattr(torch, 'xpu') and torch.xpu.is_available():
                self.device = torch.device(Config.XPU_DEVICE)
                self.is_available = True
                
                # Get GPU info
                gpu_count = torch.xpu.device_count()
                current_device = torch.xpu.current_device()
                gpu_name = torch.xpu.get_device_name(current_device)
                
                logger.info(f"✅ Intel GPU initialized: {gpu_name}")
                logger.info(f"Available XPU devices: {gpu_count}")
                logger.info(f"Using device: {self.device}")
                
                # Set memory fraction to avoid OOM
                if hasattr(torch.xpu, 'set_memory_fraction'):
                    torch.xpu.set_memory_fraction(Config.MEMORY_FRACTION)
                    logger.info(f"Set GPU memory fraction to {Config.MEMORY_FRACTION}")
                
                # Clear cache
                torch.xpu.empty_cache()
                logger.info("Intel XPU utilities ready!")
                
            else:
                logger.warning("Intel XPU not available")
                self.device = torch.device("cpu")
                self.is_available = False
            
            self._initialized = True
                
        except Exception as e:
            logger.error(f"Error in post-model GPU setup: {e}")
            self.device = torch.device("cpu")
            self.is_available = False
            self._initialized = True
    
    def get_device(self):
        """
        Get the device to use for model inference.
        Returns 'xpu' string for ipex-llm (it handles device placement automatically)
        """
        # Don't initialize here - let ipex-llm handle device selection
        # Just return the device type for reference
        return "xpu" if self.is_available else "cpu"
    
    def get_device_info(self):
        """Get detailed device information (safe to call after model loads)"""
        if not self._initialized:
            return {
                "device": "pending",
                "type": "Pending model load",
                "available": False,
                "note": "GPU info available after model loads"
            }
            
        if not self.is_available:
            return {"device": "cpu", "type": "CPU", "available": False}
        
        # Import torch locally
        import torch
        
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
    
    
    def clear_memory(self):
        """Clear GPU memory cache (safe to call after initialization)"""
        if self._initialized and self.is_available:
            # Import torch locally
            import torch
            try:
                torch.xpu.empty_cache()
                logger.info("Intel XPU memory cache cleared")
            except Exception as e:
                logger.error(f"Error clearing XPU memory: {e}")
        else:
            logger.debug("GPU not initialized or not available, skipping memory clear")

# Global instance
gpu_manager = IntelGPUManager()
