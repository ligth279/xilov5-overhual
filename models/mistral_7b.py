"""
Mistral 7B Model - Clean version for answer evaluation and hints
Uses IPEX-LLM with 4-bit quantization for Intel XPU
"""
from ipex_llm.transformers import AutoModelForCausalLM
from transformers import AutoTokenizer
import logging
import time

logger = logging.getLogger(__name__)


class MistralModel:
    """Mistral 7B model optimized for Intel XPU"""
    
    def __init__(self, config):
        """Initialize Mistral model with Intel XPU optimization"""
        import torch
        self.config = config
        self.model = None
        self.tokenizer = None
        self.device = "xpu"
        self.is_loaded = False
        
        # Load model if available
        if torch.xpu.is_available():
            self.load_model()
        else:
            logger.error("Intel XPU not available for Mistral model")
    
    def load_model(self):
        """Load Mistral model with 4-bit quantization, following phi_model pattern."""
        model_id = "mistralai/Mistral-7B-Instruct-v0.2"
        try:
            logger.info(f"Loading Mistral 7B model: {model_id}")

            # Pre-download model files to cache to avoid issues
            logger.info("Pre-downloading Mistral model files to cache...")
            AutoTokenizer.from_pretrained(
                model_id,
                cache_dir=self.config.MODEL_CACHE_DIR,
                trust_remote_code=True
            )
            logger.info("✅ Mistral model files cached")

            # Load model with IPEX-LLM 4-bit quantization from cached files
            logger.info("Loading Mistral model with IPEX-LLM 4-bit quantization...")
            self.model = AutoModelForCausalLM.from_pretrained(
                model_id,
                load_in_4bit=True,
                trust_remote_code=True,
                attn_implementation='eager',  # Avoid DynamicCache issues
                cache_dir=self.config.MODEL_CACHE_DIR
            )
            
            # Move to XPU
            self.model = self.model.to(self.device)
            
            # Load tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(
                model_id,
                cache_dir=self.config.MODEL_CACHE_DIR,
                trust_remote_code=True
            )

            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
 
            self.model.eval()
            self.is_loaded = True
            logger.info("✅ Mistral 7B loaded successfully on Intel XPU")
            
        except Exception as e:
            logger.error(f"Failed to load Mistral model '{model_id}': {e}")
            self.is_loaded = False
            raise
    
    def generate_response(self, user_message, max_new_tokens=100, temperature=0.1, 
                          top_p=0.9, system_prompt_override=None):
        """
        Generate response using Mistral 7B
        SIMPLE, CLEAN VERSION - no aggressive cleanup
        """
        import torch
        if not self.is_loaded:
            return "Error: Model not loaded"
        
        try:
            # Build prompt with Mistral's instruction format
            if system_prompt_override:
                full_prompt = f"<s>[INST] {system_prompt_override}\n\n{user_message} [/INST]"
            else:
                full_prompt = f"<s>[INST] {user_message} [/INST]"
            
            # Tokenize
            inputs = self.tokenizer(
                full_prompt,
                return_tensors="pt",
                truncation=True,
                max_length=2048
            ).to(self.device)
            
            logger.info(f"Mistral input tokens: {inputs['input_ids'].shape[1]}")
            
            # Generate
            start_time = time.time()
            
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=max_new_tokens,
                    temperature=temperature,
                    top_p=top_p,
                    do_sample=temperature > 0.0,
                    pad_token_id=self.tokenizer.eos_token_id,
                    num_beams=1,
                    use_cache=False
                    # early_stopping removed: not applicable with num_beams=1
                )
            
            generation_time = time.time() - start_time
            
            # Decode response
            generated_ids = outputs[0][inputs['input_ids'].shape[1]:]
            response_text = self.tokenizer.decode(generated_ids, skip_special_tokens=True).strip()
            
            tokens_generated = len(generated_ids)
            logger.info(f"Mistral generated {tokens_generated} tokens in {generation_time:.2f}s ({tokens_generated/generation_time:.2f} tok/s)")
            
            return response_text
            
        except Exception as e:
            logger.error(f"Mistral generation error: {e}")
            return f"Error generating response: {str(e)}"
    
    def unload(self):
        """Unload model from memory"""
        import torch
        if self.model:
            del self.model
            self.model = None
        if self.tokenizer:
            del self.tokenizer
            self.tokenizer = None
        
        import gc
        gc.collect()
        torch.xpu.empty_cache()
        
        self.is_loaded = False
        logger.info("Mistral model unloaded")
