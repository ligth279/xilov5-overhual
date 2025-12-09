"""
Mistral 7B Instruct v0.3 Model - Lightweight instruction-following model
Direct responses, fast inference

Target: Intel Arc B580 (12GB VRAM)
v5: Vulkan via llama.cpp (8-12 tok/s estimated)
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


class MistralModel(BaseAIModel):
    """
    Mistral 7B Instruct v0.3 model - lightweight and fast.
    
    Backend: Vulkan (GPU compute shaders)
    Performance: ~8-12 tok/s on Intel Arc B580 (estimated)
    VRAM: 4-5GB
    """
    
    # Model capabilities configuration
    IS_REASONING_MODEL = False  # Mistral gives direct answers
    REASONING_MARKER = None     # No reasoning separation needed
    BACKEND = "vulkan"  # v6: "openvino" or "sycl" for other implementations
    
    def __init__(self, config):
        """Initialize Mistral 7B model with Vulkan backend"""
        super().__init__(config)
        self.server_process = None
        self.server_url = "http://localhost:8080"
        # self.model_name inherited from BaseAIModel via config
        
        # Paths - Mistral 7B Instruct v0.3 (Q4_K_S quantization, 3.86GB)
        self.model_path = r"C:\Users\joseph\AppData\Local\Programs\AI Playground\resources\service\models\llm\ggufLLM\bartowski---Mistral-7B-Instruct-v0.3-GGUF\Mistral-7B-Instruct-v0.3-Q4_K_S.gguf"
        self.llama_server = rf"{os.environ['LOCALAPPDATA']}\Microsoft\WinGet\Packages\ggml.llamacpp_Microsoft.Winget.Source_8wekyb3d8bbwe\llama-server.exe"
        
        # Register cleanup on exit
        atexit.register(self.unload)

    
    def load_model(self):
        """Start llama-server with Mistral 7B model."""
        if self.server_process:
            logger.warning("Model already loaded")
            return
        
        logger.info("Starting Mistral 7B Instruct v0.3 server...")
        
        # llama-server command for Mistral with Vulkan
        cmd = [
            self.llama_server,
            "-m", self.model_path,
            "--host", "127.0.0.1",
            "--port", "8080",
            "-ngl", "99",  # Offload all layers to GPU
            "-c", "8192",  # Context window (Mistral supports 8k)
            "-t", "8",     # CPU threads for non-GPU ops
            "--n-gpu-layers", "99"
        ]
        
        # Start server process
        try:
            self.server_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=os.path.dirname(self.llama_server)
            )
            
            # Wait for server to be ready
            logger.info("Waiting for Mistral server to initialize...")
            max_wait = 120  # 120 seconds for initial load
            start_time = time.time()
            
            while time.time() - start_time < max_wait:
                try:
                    response = requests.get(f"{self.server_url}/health", timeout=2)
                    if response.status_code == 200:
                        logger.info("✅ Mistral 7B server ready!")
                        self.is_loaded = True
                        return
                except requests.exceptions.RequestException:
                    time.sleep(1)
            
            raise RuntimeError("Mistral server failed to start within 120 seconds")
            
        except Exception as e:
            logger.error(f"Failed to start Mistral server: {e}")
            if self.server_process:
                self.server_process.kill()
                self.server_process = None
            raise
    
    def unload(self):
        """Stop llama-server process"""
        if self.server_process:
            logger.info("Shutting down Mistral server...")
            try:
                self.server_process.terminate()
                self.server_process.wait(timeout=5)
            except:
                self.server_process.kill()
            finally:
                self.server_process = None
                self.is_loaded = False
    
    def generate_response(self, prompt, max_new_tokens=256, temperature=0.7, 
                         top_p=0.9, conversation_history=None, 
                         system_prompt_override=None, language_code="en"):
        """
        Generate response using Mistral 7B via llama.cpp server.
        
        Args:
            prompt: User input text
            max_new_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0.0-1.0)
            top_p: Nucleus sampling parameter
            conversation_history: List of previous messages for context
            system_prompt_override: Custom system prompt
            language_code: Language for response (Mistral supports many languages)
        
        Returns:
            Generated text response
        """
        if not self.server_process:
            raise RuntimeError("Model not loaded. Call load_model() first.")
        
        # Build messages for chat completion
        messages = []
        
        # System prompt
        system_prompt = system_prompt_override or self._get_system_prompt(language_code)
        if system_prompt:
            messages.append({
                "role": "system",
                "content": system_prompt
            })
        
        # Add conversation history (last 3 exchanges)
        if conversation_history:
            messages.extend(conversation_history[-6:])  # Last 3 Q&A pairs = 6 messages
        
        # Add current user message
        messages.append({
            "role": "user",
            "content": prompt
        })
        
        # Call llama.cpp chat completions API
        try:
            response = requests.post(
                f"{self.server_url}/v1/chat/completions",
                json={
                    "messages": messages,
                    "max_tokens": max_new_tokens,
                    "temperature": temperature,
                    "top_p": top_p,
                    "stream": False
                },
                timeout=120  # 2 minute timeout
            )
            response.raise_for_status()
            
            result = response.json()
            generated_text = result["choices"][0]["message"]["content"]
            
            # Mistral gives direct responses - no extraction needed
            return generated_text.strip()
            
        except requests.exceptions.Timeout:
            logger.error("Mistral generation timeout")
            return "I apologize, but the response took too long. Please try again."
        except Exception as e:
            logger.error(f"Mistral generation error: {e}")
            return f"An error occurred: {str(e)}"
    
    def _get_system_prompt(self, language_code):
        """Get system prompt for Mistral (supports multilingual)"""
        prompts = {
            "en": "You are a helpful, knowledgeable tutor. Provide clear, accurate, and concise answers.",
            "es": "Eres un tutor útil y conocedor. Proporciona respuestas claras, precisas y concisas.",
            "fr": "Vous êtes un tuteur utile et compétent. Fournissez des réponses claires, précises et concises.",
            "de": "Sie sind ein hilfreicher, sachkundiger Tutor. Geben Sie klare, genaue und prägnante Antworten.",
            "it": "Sei un tutor utile e competente. Fornisci risposte chiare, accurate e concise.",
            "pt": "Você é um tutor útil e conhecedor. Forneça respostas claras, precisas e concisas.",
            "ru": "Вы полезный и знающий репетитор. Предоставляйте четкие, точные и краткие ответы.",
            "ja": "あなたは親切で知識豊富な家庭教師です。明確で正確かつ簡潔な回答を提供してください。",
            "zh": "你是一位乐于助人、知识渊博的导师。提供清晰、准确、简洁的答案。",
            "ko": "당신은 도움이 되고 지식이 풍부한 튜터입니다. 명확하고 정확하며 간결한 답변을 제공하십시오.",
            "ar": "أنت معلم مفيد وذو معرفة. قدم إجابات واضحة ودقيقة وموجزة.",
            "hi": "आप एक सहायक, जानकार शिक्षक हैं। स्पष्ट, सटीक और संक्षिप्त उत्तर प्रदान करें।",
            "bn": "আপনি একজন সহায়ক, জ্ঞানী শিক্ষক। স্পষ্ট, নির্ভুল এবং সংক্ষিপ্ত উত্তর প্রদান করুন।"
        }
        return prompts.get(language_code, prompts["en"])
    
    def get_info(self):
        """Return model information"""
        return {
            "name": "Mistral 7B Instruct v0.3",
            "backend": self.BACKEND,
            "quantization": "Q4_K_S",
            "vram": "~4-5GB",
            "performance": "8-12 tok/s (estimated)",
            "context_window": "8192 tokens",
            "is_reasoning_model": self.IS_REASONING_MODEL,
            "status": "loaded" if self.server_process else "unloaded"
        }
