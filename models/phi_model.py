"""
Phi 3.5 Model wrapper optimized for Intel Arc GPU
Follows AI Playground architecture patterns for Intel XPU optimization

CRITICAL: In PyTorch 2.6+xpu, importing torch auto-loads IPEX!
This conflicts with ipex-llm which needs to load IPEX itself.
Solution: Import torch locally in methods, not at module level.
"""

# DO NOT import torch here - it auto-loads IPEX in PyTorch 2.6!
import time
import logging
from config import Config

logger = logging.getLogger(__name__)

class PhiTutor:
    def __init__(self):
        self.model = None
        self.tokenizer = None
        self.device = None  # Defer device detection to avoid import hang with PyTorch 2.1.0a0
        self.is_loaded = False
        
    def     _detect_intel_device(self):
        """
        Detect Intel XPU device availability.
        WARNING: In PyTorch 2.6, calling torch.xpu.is_available() auto-imports IPEX!
        This must only be called AFTER ipex-llm has loaded the model.
        For now, just return 'xpu' and let ipex-llm handle detection.
        """
        # Don't call torch.xpu.is_available() here - it auto-imports IPEX in PyTorch 2.6!
        # ipex-llm will auto-detect and use XPU if available
        return 'xpu'  # Let ipex-llm handle the actual detection
        
    def load_model(self):
        """Load Phi 3.5 model with Intel XPU optimization"""
        # CORRECT ORDER for PyTorch 2.6 + ipex-llm (from official docs):
        # 1. Import torch first
        # 2. Then import ipex_llm
        
        # DEBUG: Check module state at start
        import sys
        print(f"[DEBUG] load_model() START - torch loaded: {'torch' in sys.modules}, IPEX loaded: {'intel_extension_for_pytorch' in sys.modules}")
        
        # Import torch FIRST (official ipex-llm pattern for PyTorch 2.6)
        import torch
        print(f"[DEBUG] After torch import - torch loaded: {'torch' in sys.modules}, IPEX loaded: {'intel_extension_for_pytorch' in sys.modules}")
        
        try:
            # Detect device now (safe after import completes)
            if self.device is None:
                self.device = self._detect_intel_device()
            
            print(f"[DEBUG] After _detect_intel_device() - torch loaded: {'torch' in sys.modules}, IPEX loaded: {'intel_extension_for_pytorch' in sys.modules}")
            
            logger.info(f"Loading Phi 3.5 model: {Config.MODEL_NAME}")
            logger.info(f"Target device: {self.device}")
            
            Config.create_directories()
            
            print(f"[DEBUG] After create_directories() - torch loaded: {'torch' in sys.modules}, IPEX loaded: {'intel_extension_for_pytorch' in sys.modules}")
            
            # Load model FIRST (following official ipex-llm PyTorch 2.6 pattern)
            if self.device == 'xpu':
                # Intel Arc GPU - use IPEX-LLM (AI Playground pattern)
                logger.info("Loading with Intel IPEX-LLM optimization...")
                
                print(f"[DEBUG] BEFORE ipex_llm import - IPEX loaded: {'intel_extension_for_pytorch' in sys.modules}")
                
                # Import ipex_llm AFTER torch (official pattern for PyTorch 2.6)
                from ipex_llm.transformers import AutoModelForCausalLM
                
                print(f"[DEBUG] AFTER ipex_llm import - IPEX loaded: {'intel_extension_for_pytorch' in sys.modules}")
                
                # Pre-download model with standard transformers to cache all files
                from transformers import AutoTokenizer
                logger.info("Pre-downloading model files to cache...")
                print(f"[DEBUG] Downloading to cache: {Config.MODEL_CACHE_DIR}")
                AutoTokenizer.from_pretrained(
                    Config.MODEL_NAME,
                    cache_dir=Config.MODEL_CACHE_DIR,
                    trust_remote_code=True
                )
                logger.info("✅ Model files cached")
                
                # Now load with ipex-llm from cached files
                logger.info("Loading model with IPEX-LLM 4-bit quantization...")
                print(f"[DEBUG] Loading model: {Config.MODEL_NAME}")
                
                try:
                    self.model = AutoModelForCausalLM.from_pretrained(
                        Config.MODEL_NAME,
                        load_in_4bit=True,          # 4-bit quantization for Intel GPU
                        trust_remote_code=True,
                        attn_implementation='eager',  # Use eager attention to avoid DynamicCache issues
                        cache_dir=Config.MODEL_CACHE_DIR  # Use cached files
                    )
                    print(f"[DEBUG] Model loaded successfully!")
                except Exception as e:
                    print(f"[DEBUG] Model loading error: {type(e).__name__}: {e}")
                    import traceback
                    traceback.print_exc()
                    raise
                
                self.model = self.model.to('xpu')
                logger.info("✅ Model loaded with Intel XPU 4-bit optimization")
                logger.info(f"XPU Memory: {torch.xpu.memory_allocated(0) / 1024**3:.2f} GB")
                
            else:
                # CPU fallback
                import torch  # Safe to import here for CPU path
                logger.info("Loading with CPU (standard transformers)...")
                from transformers import AutoModelForCausalLM
                
                self.model = AutoModelForCausalLM.from_pretrained(
                    Config.MODEL_NAME,
                    cache_dir=Config.MODEL_CACHE_DIR,
                    torch_dtype=torch.float32,
                    trust_remote_code=True,
                    low_cpu_mem_usage=True
                )
                self.model = self.model.to('cpu')
                logger.info("✅ Model loaded on CPU")
            
            # Load tokenizer AFTER model (now safe - IPEX already loaded by ipex-llm)
            from transformers import AutoTokenizer
            logger.info("Loading tokenizer...")
            self.tokenizer = AutoTokenizer.from_pretrained(
                Config.MODEL_NAME,
                cache_dir=Config.MODEL_CACHE_DIR,
                trust_remote_code=True
            )
            
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
            
            self.model.eval()
            self.is_loaded = True
            
            # NOW it's safe to initialize GPU utilities - ipex-llm has imported IPEX
            if self.device == 'xpu':
                from utils.intel_gpu import gpu_manager
                gpu_manager.post_model_load_setup()
                logger.info("✅ GPU utilities initialized post-model-load")
            
        except ImportError as e:
            logger.error(f"❌ Missing required package: {e}")
            logger.error("Install: pip install --pre --upgrade ipex-llm[xpu] --extra-index-url https://pytorch-extension.intel.com/release-whl/stable/xpu/us/")
            raise
        except Exception as e:
            logger.error(f"❌ Error loading model: {e}")
            raise
    
    def format_prompt(self, user_message, system_message=None):
        """Format message for Phi 3.5 chat template"""
        if system_message is None:
            system_message = """You are Xilo, a helpful AI tutor.

When user says "hello" or greets you: Reply with ONE sentence like "Hello! How can I help you?" then STOP.
When explaining concepts: Use plain readable language, not LaTeX code.
Write equations simply: "E = mc²" or "flux equals Q divided by epsilon zero"
Answer the question directly, then stop writing."""

        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message}
        ]
        
        return self.tokenizer.apply_chat_template(
            messages, 
            tokenize=False, 
            add_generation_prompt=True
        )
    
    def generate_response(self, user_message, max_new_tokens=512, temperature=0.7, top_p=0.9):
        """Generate AI tutor response with Intel XPU acceleration"""
        # Import torch locally
        import torch
        
        if not self.is_loaded:
            return "Error: Model not loaded. Please wait while the model initializes."
        
        try:
            # Smart token limiting based on question complexity
            question_words = len(user_message.strip().split())
            question_lower = user_message.lower().strip()
            
            # Detect greetings and simple responses
            greetings = ['hello', 'hi', 'hey', 'thanks', 'thank you', 'bye', 'goodbye']
            if any(greeting in question_lower for greeting in greetings) and question_words <= 5:
                max_new_tokens = 80  # Short response for greetings
                temperature = 0.3    # Lower temperature = more focused/less rambling
            elif question_words <= 10:  # Short questions
                max_new_tokens = min(max_new_tokens, 200)
                temperature = 0.5
            elif question_words <= 25:  # Medium questions
                max_new_tokens = min(max_new_tokens, 400)
            # else: use provided max_new_tokens for detailed questions
            
            logger.info(f"Question words: {question_words}, Max tokens: {max_new_tokens}")
            
            # Format prompt
            prompt = self.format_prompt(user_message)
            
            # Tokenize (limit input to prevent OOM)
            inputs = self.tokenizer(
                prompt, 
                return_tensors="pt", 
                truncation=True, 
                max_length=3072  # Leave room for response
            ).to(self.device)
            
            logger.info(f"Input tokens: {inputs['input_ids'].shape[1]}")
            
            # Generate with Intel XPU optimization
            start_time = time.time()
            
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=max_new_tokens,
                    do_sample=True,
                    temperature=temperature,
                    top_p=top_p,
                    repetition_penalty=1.1,
                    pad_token_id=self.tokenizer.eos_token_id,
                    eos_token_id=self.tokenizer.eos_token_id
                    # use_cache removed - compatibility issue with transformers 4.49.0
                )
            
            generation_time = time.time() - start_time
            tokens_generated = outputs.shape[1] - inputs['input_ids'].shape[1]
            
            # Decode response
            response = self.tokenizer.decode(
                outputs[0][inputs['input_ids'].shape[1]:], 
                skip_special_tokens=True
            )
            
            logger.info(f"Generated {tokens_generated} tokens in {generation_time:.2f}s ({tokens_generated/generation_time:.2f} tok/s)")
            
            # Clean up memory
            del inputs, outputs
            if self.device == 'xpu':
                torch.xpu.empty_cache()
            
            return response.strip()
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return f"Sorry, I encountered an error: {str(e)}"
    
    def get_model_info(self):
        """Get model information"""
        if not self.is_loaded:
            return {"status": "not_loaded", "model": Config.MODEL_NAME}
        
        info = {
            "status": "loaded",
            "model": Config.MODEL_NAME,
            "device": str(self.device),
            "tokenizer_vocab_size": len(self.tokenizer)
        }
        
        if self.device == 'xpu':
            # Import torch locally
            import torch
            info["xpu_name"] = torch.xpu.get_device_name(0)
            info["xpu_memory_allocated_gb"] = torch.xpu.memory_allocated(0) / 1024**3
        
        return info

# Global model instance
phi_tutor = PhiTutor()