"""
Phi 3.5 Model wrapper optimized for Intel GPU
Handles model loading, inference, and Intel XPU acceleration
"""

import torch
import time
from transformers import AutoModelForCausalLM, AutoTokenizer, TextStreamer
import logging
from config import Config
from utils.intel_gpu import gpu_manager

logger = logging.getLogger(__name__)

class PhiTutor:
    def __init__(self):
        self.model = None
        self.tokenizer = None
        self.device = gpu_manager.get_device()
        self.is_loaded = False
        
    def load_model(self):
        """Load Phi 3.5 model with Intel GPU optimization"""
        try:
            logger.info(f"Loading Phi 3.5 model: {Config.MODEL_NAME}")
            logger.info(f"Target device: {self.device}")
            
            # Create cache directory
            Config.create_directories()
            
            # Load tokenizer
            logger.info("Loading tokenizer...")
            self.tokenizer = AutoTokenizer.from_pretrained(
                Config.MODEL_NAME,
                cache_dir=Config.MODEL_CACHE_DIR,
                trust_remote_code=True
            )
            
            # Set padding token
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
            
            # Load model
            logger.info("Loading model...")
            self.model = AutoModelForCausalLM.from_pretrained(
                Config.MODEL_NAME,
                cache_dir=Config.MODEL_CACHE_DIR,
                torch_dtype=torch.float16 if gpu_manager.is_available else torch.float32,
                trust_remote_code=True,
                device_map="auto" if not gpu_manager.is_available else None
            )
            
            # Apply Intel GPU optimizations
            if gpu_manager.is_available:
                logger.info("Applying Intel XPU optimizations...")
                self.model = gpu_manager.optimize_model(self.model)
            else:
                logger.info("Moving model to CPU...")
                self.model = self.model.to(self.device)
            
            # Set model to evaluation mode
            self.model.eval()
            
            self.is_loaded = True
            logger.info("✅ Phi 3.5 model loaded successfully!")
            
            # Log device info
            device_info = gpu_manager.get_device_info()
            logger.info(f"Device info: {device_info}")
            
        except Exception as e:
            logger.error(f"❌ Error loading model: {e}")
            self.is_loaded = False
            raise e
    
    def format_prompt(self, user_message, system_message=None):
        """Format message for Phi 3.5 chat template"""
        if system_message is None:
            system_message = """You are Xilo, an intelligent AI tutor. Your role is to:
            
1. Provide clear, educational explanations
2. Break down complex topics into understandable parts
3. Use examples and analogies when helpful
4. Encourage learning and critical thinking
5. Ask follow-up questions to deepen understanding
6. Be patient and supportive

Always aim to teach rather than just provide answers. Make learning engaging and interactive."""

        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message}
        ]
        
        return self.tokenizer.apply_chat_template(
            messages, 
            tokenize=False, 
            add_generation_prompt=True
        )
    
    def generate_response(self, user_message, max_length=None, temperature=None, top_p=None):
        """Generate AI tutor response"""
        logger.info("🔄 generate_response called")
        
        if not self.is_loaded:
            logger.error("❌ Model not loaded!")
            return "Error: Model not loaded. Please wait while the model initializes."
        
        logger.info("✅ Model is loaded, proceeding...")
        
        try:
            # Set parameters
            max_length = max_length or Config.MAX_LENGTH
            temperature = temperature or Config.TEMPERATURE
            top_p = top_p or Config.TOP_P
            
            logger.info(f"📊 Parameters set: max_len={max_length}, temp={temperature}, top_p={top_p}")
            
            # Format prompt
            logger.info("🔤 Starting prompt formatting...")
            prompt = self.format_prompt(user_message)
            logger.info(f"✅ Formatted prompt length: {len(prompt)} chars")
            
            # Tokenize input
            inputs = self.tokenizer(
                prompt, 
                return_tensors="pt", 
                truncation=True, 
                max_length=max_length//2
            ).to(self.device)
            
            logger.info(f"Input tokens shape: {inputs['input_ids'].shape}")
            logger.info(f"Input device: {inputs['input_ids'].device}")
            logger.info(f"Model device: {next(self.model.parameters()).device}")
            
            # Generate response
            with torch.no_grad():
                logger.info("Starting model generation...")
                logger.info(f"Generation params: max_new_tokens={min(512, max_length//4)}, do_sample=False")
                
                start_time = time.time()
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=64,  # Much smaller for testing - only 64 tokens
                    do_sample=False,  # Use greedy decoding - no temperature needed
                    pad_token_id=self.tokenizer.eos_token_id,
                    eos_token_id=self.tokenizer.eos_token_id,
                    use_cache=True,
                    num_beams=1  # Single beam for simplicity
                )
                end_time = time.time()
                logger.info(f"✅ Model generation completed in {end_time - start_time:.2f} seconds!")
                logger.info(f"Output shape: {outputs.shape}")
            
            # Decode response
            response = self.tokenizer.decode(
                outputs[0][inputs['input_ids'].shape[1]:], 
                skip_special_tokens=True
            )
            logger.info(f"Raw generated tokens: {outputs[0][inputs['input_ids'].shape[1]:]}")
            logger.info(f"Decoded response length: {len(response)} chars")
            logger.info(f"Decoded response content: '{response}'")
            
            # Clean up memory
            del inputs, outputs
            gpu_manager.clear_memory()
            
            final_response = response.strip()
            logger.info(f"Final cleaned response: '{final_response}'")
            return final_response
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return f"Sorry, I encountered an error while generating a response: {str(e)}"
    
    def get_model_info(self):
        """Get model information"""
        if not self.is_loaded:
            return {"status": "not_loaded", "model": Config.MODEL_NAME}
        
        device_info = gpu_manager.get_device_info()
        
        return {
            "status": "loaded",
            "model": Config.MODEL_NAME,
            "device": device_info,
            "tokenizer_vocab_size": len(self.tokenizer),
            "max_length": Config.MAX_LENGTH
        }

# Global model instance
phi_tutor = PhiTutor()
