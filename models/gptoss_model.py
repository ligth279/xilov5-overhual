"""
GPT-OSS 20B - Reasoning model (13.9GB VRAM)
Shows chain-of-thought, extracts final answer

Target: Intel Arc B580
v5: Vulkan (llama.cpp) - 4-7 tok/s
v6: OpenVINO or SYCL - 8-12 tok/s target via XMX engines
"""
import subprocess
import requests
import logging
import time
import os
import atexit
from models.base_model import BaseAIModel

logger = logging.getLogger(__name__)

class GPTOSSModel(BaseAIModel):
    """
    GPT-OSS 20B model using llama-server.exe with Vulkan backend.
    
    Backend: Vulkan (GPU compute shaders)
    Performance: ~4-7 tok/s on Intel Arc B580
    VRAM: 13.9GB
    """
    
    # Model capabilities configuration
    IS_REASONING_MODEL = True  # GPT-OSS shows chain-of-thought reasoning
    REASONING_MARKER = '<|start|>assistant<|channel|>final<|message|>'  # Separator between reasoning and answer
    BACKEND = "vulkan"  # v6: "openvino" or "sycl" for other implementations
    
    def __init__(self, config):
        """Initialize GPT-OSS model with Vulkan backend"""
        super().__init__(config)
        self.server_process = None
        self.server_url = "http://localhost:8081"
        self.model_name = "GPT-OSS 20B (Vulkan)"
        
        # Paths
        self.model_path = r"C:\Users\joseph\AppData\Local\Programs\AI Playground\resources\service\models\llm\ggufLLM\unsloth---gpt-oss-20b-GGUF\gpt-oss-20b-Q8_0.gguf"
        self.llama_server = rf"{os.environ['LOCALAPPDATA']}\Microsoft\WinGet\Packages\ggml.llamacpp_Microsoft.Winget.Source_8wekyb3d8bbwe\llama-server.exe"
        
        # WARNING: This model requires 13.9GB VRAM
        # No other models should be loaded simultaneously
        
        # Register cleanup on exit
        atexit.register(self.unload)
    
    def load_model(self):
        """Start llama-server with GPT-OSS 20B model."""
        if self.server_process is not None and self.is_loaded:
            return self.model_info
        
        try:
            start_time = time.time()
            logger.info("Starting llama-server with GPT-OSS 20B...")
            
            # Verify files exist
            if not os.path.exists(self.model_path):
                raise FileNotFoundError(f"Model not found: {self.model_path}")
            if not os.path.exists(self.llama_server):
                raise FileNotFoundError(f"llama-server.exe not found: {self.llama_server}")
            
            # Start llama-server with GPU acceleration
            # -ngl -1 = offload all layers to GPU (Vulkan backend)
            # Chat template auto-detected from GGUF metadata
            cmd = [
                self.llama_server,
                "-m", self.model_path,
                "-c", "2048",        # Context size
                "-ngl", "-1",        # GPU layers (all)
                "--port", "8081",
                "--host", "localhost"
                # No --chat-template needed: GGUF has embedded template
            ]
            
            self.server_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=os.path.dirname(self.llama_server)
            )
            
            # Wait for server to start (check /health endpoint)
            # Loading 13.9GB model can take 60-120 seconds
            logger.info("Waiting for llama-server to start (this takes 1-2 minutes for 13.9GB model)...")
            for i in range(120):  # 120 second timeout (2 minutes)
                try:
                    response = requests.get(f"{self.server_url}/health", timeout=2)
                    if response.status_code == 200:
                        logger.info(f"Server responded after {i+1} seconds")
                        break
                except:
                    pass
                
                # Check if process crashed early
                if self.server_process.poll() is not None:
                    stderr = self.server_process.stderr.read() if self.server_process.stderr else b""
                    stdout = self.server_process.stdout.read() if self.server_process.stdout else b""
                    logger.error(f"llama-server crashed early!")
                    logger.error(f"STDOUT: {stdout.decode()}")
                    logger.error(f"STDERR: {stderr.decode()}")
                    raise RuntimeError(f"llama-server crashed: {stderr.decode()}")
                
                # Log progress every 10 seconds
                if (i + 1) % 10 == 0:
                    logger.info(f"Still loading... {i+1}s elapsed")
                
                time.sleep(1)
            else:
                # Timeout reached - capture output for debugging
                if self.server_process.poll() is not None:
                    stderr = self.server_process.stderr.read() if self.server_process.stderr else b""
                    stdout = self.server_process.stdout.read() if self.server_process.stdout else b""
                    logger.error(f"llama-server process ended")
                    logger.error(f"STDOUT: {stdout.decode()}")
                    logger.error(f"STDERR: {stderr.decode()}")
                    raise RuntimeError(f"llama-server crashed: {stderr.decode()}")
                raise TimeoutError("llama-server failed to start within 2 minutes")
            
            load_time = time.time() - start_time
            self.is_loaded = True
            logger.info(f"✅ GPT-OSS 20B server ready in {load_time:.2f}s (13.9GB VRAM)")
            
            self.model_info = {
                "status": "ready",
                "model_name": "GPT-OSS 20B",
                "vram_usage": "~13.9GB",
                "load_time": f"{load_time:.2f}s",
                "quantization": "Q8_0 (8-bit)",
                "gpu_layers": "All (-1)",
                "library": "llama-server.exe (Vulkan)",
                "server_url": self.server_url
            }
            return self.model_info
            
        except Exception as e:
            logger.error(f"Failed to start GPT-OSS server: {e}")
            self.is_loaded = False
            if self.server_process:
                self.server_process.kill()
                self.server_process = None
            raise
    
    def generate_response(self, user_message, max_new_tokens=512, temperature=0.7, 
                          top_p=0.9, system_prompt_override=None, conversation_history=None, **kwargs):
        """
        Generate response using GPT-OSS 20B with native chat template.
        Manually formats with GPT-OSS markers to ensure reasoning extraction works.
        
        Args:
            user_message: User input text
            max_new_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0.0-1.0)
            top_p: Nucleus sampling parameter
            system_prompt_override: Optional system prompt
            conversation_history: List of previous messages [{"role": "user"/"assistant", "content": "..."}]
            
        Returns:
            str: Generated response (with reasoning extracted)
        """
        if not self.is_loaded or self.server_process is None:
            return "Error: Model server not running"
        
        try:
            # Build prompt with GPT-OSS native format
            # Format: <|start|>system<|message|>...<|end|><|start|>user<|message|>...<|end|><|start|>assistant
            prompt = "<|start|>system<|message|>"
            
            if system_prompt_override:
                prompt += system_prompt_override
            else:
                # Default system prompt - tells model to think internally but respond cleanly
                prompt += "You are a helpful AI assistant. Think through problems step-by-step internally, but provide only clear, direct answers to the user without showing your reasoning process."
            
            prompt += "<|end|>"
            
            # Add conversation history (last 3 exchanges)
            if conversation_history:
                for msg in conversation_history[-6:]:  # Last 3 user+assistant pairs
                    role = msg["role"]
                    content = msg["content"]
                    if role == "user":
                        prompt += f"<|start|>user<|message|>{content}<|end|>"
                    elif role == "assistant":
                        # Assistant messages have final channel (no reasoning in history)
                        prompt += f"<|start|>assistant<|channel|>final<|message|>{content}<|end|>"
            
            # Add current user message
            prompt += f"<|start|>user<|message|>{user_message}<|end|>"
            
            # Start assistant response - model will add channel tags
            prompt += "<|start|>assistant"
            
            logger.info(f"GPT-OSS input length: {len(prompt)} chars")
            
            # Call llama-server /completion endpoint (raw completion, not chat)
            start_time = time.time()
            
            payload = {
                "prompt": prompt,
                "n_predict": max_new_tokens,
                "temperature": temperature,
                "top_p": top_p,
                "stop": ["<|end|>", "<|start|>user"]  # Stop at end tag or new user message
            }
            
            response = requests.post(
                f"{self.server_url}/completion",
                json=payload,
                timeout=120  # Increased for longer conversations
            )
            response.raise_for_status()
            
            result = response.json()
            response_text = result.get("content", "")
            
            generation_time = time.time() - start_time
            tokens_generated = result.get("tokens_predicted", 0)
            
            logger.info(f"GPT-OSS generated {tokens_generated} tokens in {generation_time:.2f}s ({tokens_generated/generation_time:.2f} tok/s)")
            
            # GPT-OSS is a reasoning model - extract only the final answer
            # Look for <|channel|>final<|message|> marker
            cleaned_response = self._extract_final_answer(response_text)
            
            return cleaned_response.strip()
            
        except Exception as e:
            logger.error(f"GPT-OSS generation error: {e}")
            return f"Error generating response: {str(e)}"
    
    def _extract_final_answer(self, response_text):
        """
        Extract final answer from GPT-OSS output.
        
        GPT-OSS structure: [REASONING SECTION] then [ANSWER SECTION]
        Reasoning comes first (variable length), answer comes after.
        
        Strategy: Keep skipping lines while they contain reasoning phrases.
        Once we hit a line WITHOUT reasoning phrases = answer starts there.
        """
        # Remove any template tags if model outputs them literally
        response_text = response_text.replace("<|channel|>analysis<|message|>", "")
        response_text = response_text.replace("<|channel|>final<|message|>", "")
        response_text = response_text.replace("<|end|>", "")
        
        lines = response_text.strip().split('\n')
        
        # Meta-reasoning phrases (indicates line is still reasoning, not answer)
        meta_phrases = [
            "we need to", "we should", "i need to", "i should",
            "let me", "let's", "so we", "thus we",
            "the student's answer", "the student answer",
            "the correct answer is", "the answer is",
            "the difference", "wait", "actually", 
            "spelled", " vs ", "missing the",
            "the hint should", "give a hint", "provide a hint"
        ]
        
        # Find where reasoning ends (first line without meta-phrases)
        answer_start_index = 0
        
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue  # Skip empty lines
            
            line_lower = line.lower()
            
            # Check if this line is still reasoning
            is_reasoning = any(phrase in line_lower for phrase in meta_phrases)
            
            if is_reasoning:
                # Still in reasoning section, continue skipping
                answer_start_index = i + 1
            else:
                # First non-reasoning line found = answer starts here
                answer_start_index = i
                break
        
        # Get everything from answer start onwards
        answer_lines = [line.strip() for line in lines[answer_start_index:] if line.strip()]
        
        if answer_lines:
            result = '\n'.join(answer_lines).strip()
            skipped = answer_start_index
            logger.info(f"✓ Extracted answer: {len(result)} chars (skipped {skipped} reasoning lines)")
            return result
        
        # Fallback: all lines were reasoning? Return everything
        logger.warning(f"⚠ No answer found after reasoning, returning full text")
        return response_text.strip()
    
    def unload(self):
        """Stop llama-server and free GPU resources"""
        if self.server_process:
            logger.info("Stopping llama-server...")
            try:
                self.server_process.terminate()
                self.server_process.wait(timeout=5)
            except:
                self.server_process.kill()
            self.server_process = None
        
        self.is_loaded = False
        logger.info("GPT-OSS 20B server stopped, 13.9GB VRAM freed")
    
    def get_info(self):
        """Get model information"""
        return {
            'name': self.model_name,
            'loaded': self.is_loaded,
            'device': self.device,
            'vram_usage': '13.9GB',
            'format': 'GGUF (Q8_0)',
            'exclusive': True  # Requires exclusive GPU usage
        }
