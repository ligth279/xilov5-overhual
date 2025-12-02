"""
GPT-OSS 20B Model - GGUF format from AI Playground
Uses llama-cpp-python with Intel SYCL for native XPU acceleration
"""
from llama_cpp import Llama
import logging
import time
import os

logger = logging.getLogger(__name__)


class GPTOSSModel:
    """GPT-OSS 20B model using llama-cpp-python with Intel SYCL"""
    
    def __init__(self, config):
        """Initialize GPT-OSS model"""
        self.config = config
        self.model = None
        self.device = "xpu"
        self.is_loaded = False
        self.model_name = "GPT-OSS 20B (13.9GB)"
        
        # Model path
        self.model_path = r"C:\Users\joseph\AppData\Local\Programs\AI Playground\resources\service\models\llm\ggufLLM\unsloth---gpt-oss-20b-GGUF\gpt-oss-20b-Q8_0.gguf"
        
        # WARNING: This model requires 13.9GB VRAM
        self.model_info = {}
    
    def load_model(self):
        """Load GPT-OSS 20B with Intel XPU acceleration."""
        if self.model is not None:
            return self.model_info
        
        try:
            start_time = time.time()
            logger.info("Loading GPT-OSS 20B with Intel SYCL...")
            
            # Verify model file exists
            if not os.path.exists(self.model_path):
                raise FileNotFoundError(f"Model not found: {self.model_path}")
            
            # Load with llama-cpp-python (SYCL backend)
            # n_gpu_layers=-1: Offload all layers to Intel XPU
            # n_ctx=2048: Context window
            self.model = Llama(
                model_path=self.model_path,
                n_gpu_layers=-1,      # Full GPU offloading via SYCL
                n_ctx=2048,           # Context size
                n_threads=4,          # CPU threads for host operations
                verbose=True
            )
            
            load_time = time.time() - start_time
            self.is_loaded = True
            logger.info(f"✅ GPT-OSS 20B loaded in {load_time:.2f}s (Intel XPU via SYCL)")
            
            self.model_info = {
                "status": "ready",
                "model_name": "GPT-OSS 20B",
                "vram_usage": "~13.9GB",
                "load_time": f"{load_time:.2f}s",
                "quantization": "Q8_0 (8-bit)",
                "gpu_layers": "All (-1)",
                "backend": "Intel SYCL/Level-Zero",
                "device": "Intel Arc B580"
            }
            return self.model_info
            
        except Exception as e:
            logger.error(f"Failed to load GPT-OSS: {e}")
            self.is_loaded = False
            raise
    
    def generate_response(self, user_message, max_new_tokens=512, temperature=0.7, 
                          top_p=0.9, system_prompt_override=None, **kwargs):
        """
        Generate response using GPT-OSS 20B
        
        Args:
            user_message: User input text
            max_new_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0.0-1.0)
            top_p: Nucleus sampling parameter
            system_prompt_override: Optional system prompt
            
        Returns:
            str: Generated response
        """
        if not self.is_loaded or self.model is None:
            return "Error: Model not loaded"
        
        try:
            # Build prompt
            if system_prompt_override:
                full_prompt = f"{system_prompt_override}\n\nUser: {user_message}\nAssistant:"
            else:
                full_prompt = f"User: {user_message}\nAssistant:"
            
            logger.info(f"GPT-OSS input length: {len(full_prompt)} chars")
            
            # Generate using llama-cpp-python
            start_time = time.time()
            
            output = self.model(
                full_prompt,
                max_tokens=max_new_tokens,
                temperature=temperature,
                top_p=top_p,
                stop=["User:", "\n\n\n"],
                echo=False
            )
            
            generation_time = time.time() - start_time
            response_text = output['choices'][0]['text'].strip()
            tokens_generated = output['usage']['completion_tokens']
            
            logger.info(f"GPT-OSS generated {tokens_generated} tokens in {generation_time:.2f}s ({tokens_generated/generation_time:.2f} tok/s)")
            
            return response_text
            
        except Exception as e:
            logger.error(f"GPT-OSS generation error: {e}")
            return f"Error generating response: {str(e)}"
    
    def unload(self):
        """Unload model and free GPU memory"""
        if self.model:
            del self.model
            self.model = None
        
        import gc
        gc.collect()
        
        self.is_loaded = False
        logger.info("GPT-OSS 20B unloaded, 13.9GB VRAM freed")
    
    def get_info(self):
        """Get model information"""
        return {
            'name': self.model_name,
            'loaded': self.is_loaded,
            'device': self.device,
            'vram_usage': '13.9GB',
            'format': 'GGUF (Q8_0)',
            'exclusive': True,
            'backend': 'Intel SYCL'
        }
