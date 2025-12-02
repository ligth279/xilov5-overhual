"""
Base Model Interface - v5.09.00
Abstract base class for all AI model implementations

Target Hardware: Intel Arc B580 (12GB dedicated + 8GB shared)
v5: Vulkan backend via llama.cpp (4-7 tok/s)
v6: OpenVINO or SYCL backends for XMX acceleration (8-12 tok/s target)
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)


class BaseAIModel(ABC):
    """
    Abstract base class for all AI models in Xilo.
    All model implementations must inherit from this class.
    
    v6: Add OpenVINO/SYCL backends for faster inference on Intel Arc
    """
    
    # Model capability flags (override in subclass)
    IS_REASONING_MODEL: bool = False
    REASONING_MARKER: Optional[str] = None
    BACKEND: str = "unknown"  # "vulkan", "openvino", "sycl", "cuda", "rocm"
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize model with configuration"""
        self.config = config
        self.model = None
        self.tokenizer = None
        self.device = "xpu"  # v5: XPU, v6: auto-detect
        self.is_loaded = False
        self.model_name = "Base Model"
        self.model_info: Dict[str, Any] = {}
    
    @abstractmethod
    def load_model(self) -> Dict[str, Any]:
        """
        Load model into memory and prepare for inference.
        
        v6 Note: Override to support backend-specific loading
        (OpenVINO IR, SYCL native, Vulkan GGUF, etc.)
        
        Returns:
            dict: Model information with keys:
                - status: "ready" or "error"
                - model_name: Human-readable name
                - vram_usage: VRAM usage estimate
                - load_time: Load time in seconds
                - backend: Backend used
        
        Must set self.is_loaded = True on success.
        """
        pass
    
    @abstractmethod
    def generate_response(
        self,
        user_message: str,
        max_new_tokens: int = 512,
        temperature: float = 0.7,
        top_p: float = 0.9,
        system_prompt_override: Optional[str] = None,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        **kwargs
    ) -> str:
        """
        Generate response from user message.
        
        Args:
            user_message: The user's input text
            max_new_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0.0 = greedy, 1.0 = creative)
            top_p: Nucleus sampling parameter
            system_prompt_override: Optional system prompt to override defaults
            conversation_history: List of previous messages [{"role": "user", "content": "..."}]
            **kwargs: Additional model-specific parameters
            
        Returns:
            str: Generated response text
        """
        pass
    
    @abstractmethod
    def unload(self) -> None:
        """
        Unload model from memory and free GPU resources.
        Must set self.is_loaded = False.
        """
        pass
    
    # Helper methods
    def get_info(self) -> Dict[str, Any]:
        """Get model information"""
        return self.model_info if self.model_info else {
            'name': self.model_name,
            'loaded': self.is_loaded,
            'device': self.device,
            'backend': self.BACKEND
        }
    
    def get_model_info(self) -> Dict[str, Any]:
        """Alias for get_info()"""
        return self.get_info()
    
    def is_ready(self) -> bool:
        """Check if model is loaded"""
        return self.is_loaded
    
    def supports_reasoning(self) -> bool:
        """Check if this is a reasoning model"""
        return self.IS_REASONING_MODEL
    
    def get_backend(self) -> str:
        """Get backend identifier"""
        return self.BACKEND
    
    def validate_loaded(self):
        """Check if model is loaded, return error message if not"""
        if not self.is_loaded:
            logger.error(f"{self.model_name} not loaded")
            return f"Error: {self.model_name} not loaded"
        return None


class ModelFactory:
    """
    Factory for creating model instances with backend selection.
    
    Target: Intel Arc B580 optimization
    v5: Vulkan only (4-7 tok/s)
    v6: OpenVINO or SYCL for XMX acceleration (8-12 tok/s target)
    
    Example v6 usage:
        backend = ModelFactory.get_recommended_backend()  # "openvino" or "sycl" or "vulkan"
        model = ModelFactory.create_model("gpt-oss-20b", backend=backend)
    """
    
    @staticmethod
    def create_model(
        model_name: str,
        backend: str = "auto",
        config: Optional[Dict[str, Any]] = None
    ) -> BaseAIModel:
        """
        Create model instance with specified backend.
        
        Args:
            model_name: Model identifier ("gpt-oss-20b", "llama-3.1-8b")
            backend: Backend preference ("vulkan", "openvino", "sycl", "cuda", "auto")
            config: Configuration dictionary
        
        Returns:
            BaseAIModel: Model instance
        
        Raises:
            ValueError: If model/backend combination not supported
        """
        if config is None:
            config = {}
        
        # v5.09.00: Auto = Vulkan
        if backend == "auto":
            backend = "vulkan"
        
        logger.info(f"Creating {model_name} model with {backend} backend")
        
        # GPT-OSS 20B
        if model_name.lower() in ["gpt-oss-20b", "gptoss", "gpt-oss"]:
            if backend == "vulkan":
                from models.gptoss_model import GPTOSSModel
                return GPTOSSModel(config)
            # v6: Uncomment when implemented
            # elif backend == "openvino":
            #     from models.gptoss_openvino import GPTOSSOpenVINO
            #     return GPTOSSOpenVINO(config)
            # elif backend == "sycl":
            #     from models.gptoss_sycl import GPTOSSSYCL
            #     return GPTOSSSYCL(config)
            else:
                raise ValueError(f"Backend '{backend}' not available for GPT-OSS (v5: vulkan only)")
        
        # Llama 3.1 8B
        elif model_name.lower() in ["llama-3.1-8b", "llama3.1", "llama"]:
            if backend == "vulkan":
                from models.llama31_model import Llama31Model
                return Llama31Model(config)
            # v6: Add alternative backends
            else:
                raise ValueError(f"Backend '{backend}' not available for Llama 3.1 (v5: vulkan only)")
        
        else:
            raise ValueError(f"Model '{model_name}' not recognized. Available: gpt-oss-20b, llama-3.1-8b")
    
    @staticmethod
    def list_available_backends() -> List[str]:
        """
        List available backends for Intel Arc B580.
        
        Returns:
            list: Available backend identifiers
        """
        backends = ["vulkan"]  # v5: Vulkan only
        
        # v6: Check for Intel-optimized backends
        # try:
        #     import openvino
        #     backends.append("openvino")
        #     logger.info("OpenVINO backend available (XMX acceleration)")
        # except ImportError:
        #     pass
        #
        # try:
        #     import intel_extension_for_pytorch as ipex
        #     import torch
        #     if torch.xpu.is_available():
        #         backends.append("sycl")
        #         logger.info("SYCL backend available (native Intel)")
        # except ImportError:
        #     pass
        
        return backends
        #     pass
        #
        # try:
        #     import torch
        #     if hasattr(torch, 'hip') and torch.hip.is_available():
        #         backends.append("rocm")
        #         logger.info("ROCm backend available")
        # except (ImportError, AttributeError):
        
        return backends
    
    @staticmethod
    def get_recommended_backend() -> str:
        """
        Get recommended backend for Intel Arc B580.
        
        Priority: openvino > sycl > vulkan
        
        Returns:
            str: Backend identifier
        """
        # v5: Always Vulkan
        return "vulkan"
        
        # v6: Intel Arc optimization priority
        # backends = ModelFactory.list_available_backends()
        # 
        # if "openvino" in backends:
        #     return "openvino"  # Best: XMX acceleration (8-12 tok/s target)
        # elif "sycl" in backends:
        #     return "sycl"      # Good: Native Intel (7-10 tok/s)
        # else:
        #     return "vulkan"    # Fallback: Compute shaders (4-7 tok/s)

