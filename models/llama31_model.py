"""
Llama 3.1 8B Model - Direct instruction-following model
No reasoning chains - gives clean, direct responses

Target: Intel Arc B580 (12GB VRAM)
v5: Vulkan via llama.cpp (6-10 tok/s estimated)
v6: OpenVINO or SYCL for XMX engines (faster inference)
"""
import subprocess
import requests
import logging
import time
import os
import atexit
from models.base_model import BaseAIModel

logger = logging.getLogger(__name__)


class Llama31Model(BaseAIModel):
    """
    Llama 3.1 8B Instruct model - direct responses without reasoning.
    
    Backend: Vulkan (GPU compute shaders)
    Performance: ~6-10 tok/s on Intel Arc B580 (estimated)
    VRAM: 8-9GB
    """
    
    # Model capabilities configuration
    IS_REASONING_MODEL = False  # Llama 3.1 gives direct answers
    REASONING_MARKER = None     # No reasoning separation needed
    BACKEND = "vulkan"  # v6: "openvino" or "sycl" for other implementations
    
    def __init__(self, config):
        """Initialize Llama 3.1 model with Vulkan backend"""
        super().__init__(config)
        self.server_process = None
        self.server_url = "http://localhost:8080"
        # self.model_name inherited from BaseAIModel via config
        
        # Paths - Llama 3.1 8B Instruct (Q5_K_S quantization, 5.21GB)
        self.model_path = r"C:\Users\joseph\AppData\Local\Programs\AI Playground\resources\service\models\llm\ggufLLM\bartowski---Meta-Llama-3.1-8B-Instruct-GGUF\Meta-Llama-3.1-8B-Instruct-Q5_K_S.gguf"
        self.llama_server = rf"{os.environ['LOCALAPPDATA']}\Microsoft\WinGet\Packages\ggml.llamacpp_Microsoft.Winget.Source_8wekyb3d8bbwe\llama-server.exe"
        
        # Register cleanup on exit
        atexit.register(self.unload)

    
    def load_model(self):
        """Start llama-server with Llama 3.1 model."""
        if self.is_loaded:
            return self.model_info
        
        try:
            logger.info("Starting llama-server with Llama 3.1 8B...")
            
            # Check if server is already running
            try:
                response = requests.get(f"{self.server_url}/health", timeout=2)
                if response.status_code == 200:
                    logger.warning("llama-server already running, reusing existing server")
                    self.is_loaded = True
                    return {"status": "ready", "model_name": "Llama 3.1 8B Instruct (Vulkan)"}
            except:
                pass
            
            if not os.path.exists(self.llama_server):
                raise FileNotFoundError(f"llama-server.exe not found: {self.llama_server}")
            
            # Start llama-server with GPU acceleration
            # Llama 3.1 uses standard chat template
            cmd = [
                self.llama_server,
                "-m", self.model_path,
                "-c", "4096",        # Context size (Llama 3.1 supports 128K but 4K is enough)
                "-ngl", "-1",        # GPU layers (all)
                "--port", "8080",
                "--host", "localhost"
            ]
            
            self.server_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=os.path.dirname(self.llama_server)
            )
            
            start_time = time.time()
            
            # Wait for server to start
            logger.info("Waiting for llama-server to start (Llama 3.1 is ~5GB)...")
            for i in range(120):  # 120 second timeout for initial load
                try:
                    response = requests.get(f"{self.server_url}/health", timeout=2)
                    if response.status_code == 200:
                        logger.info(f"Server responded after {i+1} seconds")
                        break
                except:
                    pass
                
                if (i + 1) % 10 == 0:
                    logger.info(f"Still loading... {i+1}s elapsed")
                
                time.sleep(1)
            else:
                if self.server_process.poll() is not None:
                    stderr = self.server_process.stderr.read() if self.server_process.stderr else b""
                    raise RuntimeError(f"llama-server crashed: {stderr.decode()}")
                raise TimeoutError("llama-server failed to start within 120 seconds")
            
            load_time = time.time() - start_time
            self.is_loaded = True
            logger.info(f"✅ Llama 3.1 8B ready in {load_time:.2f}s")
            
            self.model_info = {
                "status": "ready",
                "model_name": "Llama 3.1 8B Instruct (Vulkan)",
                "vram_usage": "~8-9GB",
                "load_time": f"{load_time:.2f}s",
                "quantization": "Q8_0 (8-bit)",
                "gpu_layers": "All (-1)",
                "library": "llama-server.exe (Vulkan)",
                "server_url": self.server_url
            }
            self.is_loaded = True
            return self.model_info
            
        except Exception as e:
            logger.error(f"Failed to load Llama 3.1: {e}")
            if self.server_process:
                self.server_process.kill()
                self.server_process = None
            raise
    
    def generate_response(self, user_message, max_new_tokens=512, temperature=0.7, 
                          top_p=0.9, system_prompt_override=None, conversation_history=None, **kwargs):
        """
        Generate response using Llama 3.1 8B via llama-server
        
        Args:
            user_message: User input text
            max_new_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0.0-1.0)
            top_p: Nucleus sampling parameter
            system_prompt_override: Optional system prompt
            conversation_history: List of previous messages
            
        Returns:
            str: Generated response (direct answer, no reasoning)
        """
        if not self.is_loaded or self.server_process is None:
            return "Error: Model server not running"
        
        try:
            # Build prompt with Llama 3.1 format
            full_prompt = ""
            
            # Add system prompt
            if system_prompt_override:
                full_prompt = f"<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n\n{system_prompt_override}<|eot_id|>"
            else:
                full_prompt = "<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n\nYou are a helpful AI assistant.<|eot_id|>"
            
            # Add conversation history
            if conversation_history:
                for msg in conversation_history[-6:]:  # Last 3 exchanges
                    role = "user" if msg["role"] == "user" else "assistant"
                    full_prompt += f"<|start_header_id|>{role}<|end_header_id|>\n\n{msg['content']}<|eot_id|>"
            
            # Add current user message
            full_prompt += f"<|start_header_id|>user<|end_header_id|>\n\n{user_message}<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n\n"
            
            logger.info(f"Llama 3.1 input length: {len(full_prompt)} chars")
            
            # Call llama-server /completion endpoint
            start_time = time.time()
            
            payload = {
                "prompt": full_prompt,
                "n_predict": max_new_tokens,
                "temperature": temperature,
                "top_p": top_p,
                "stop": ["<|eot_id|>", "<|end_of_text|>"]
            }
            
            response = requests.post(
                f"{self.server_url}/completion",
                json=payload,
                timeout=120
            )
            response.raise_for_status()
            
            result = response.json()
            response_text = result.get("content", "")
            
            generation_time = time.time() - start_time
            tokens_generated = result.get("tokens_predicted", 0)
            
            logger.info(f"Llama 3.1 generated {tokens_generated} tokens in {generation_time:.2f}s ({tokens_generated/generation_time:.2f} tok/s)")
            
            # Llama 3.1 gives direct responses - no reasoning extraction needed
            return response_text.strip()
            
        except Exception as e:
            logger.error(f"Llama 3.1 generation error: {e}")
            return f"Error generating response: {str(e)}"
    
    def unload(self):
        """Stop llama-server and free GPU resources"""
        if self.server_process:
            logger.info("Stopping llama-server...")
            try:
                self.server_process.terminate()
                self.server_process.wait(timeout=5)
            except:
                self.server_process.kill()
            finally:
                self.server_process = None
                self.is_loaded = False
                self.is_loaded = False
                logger.info("Llama 3.1 8B server stopped")
