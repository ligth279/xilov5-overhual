import os

class Config:
    # Application version
    VERSION = "5.09.00"  # Final v5 release - Model architecture overhaul
    
    # Model configuration
    MODEL_NAME = "GPT-OSS 20B"  # Current: GPT-OSS 20B (reasoning model)
    # MODEL_NAME = "Llama 3.1 8B"  # Alternative: Llama 3.1 (direct responses)
    MAX_LENGTH = 3072  # Increased for better educational content
    TEMPERATURE = 0.7
    TOP_P = 0.9
    
    # Intel GPU configuration
    USE_XPU = True
    XPU_DEVICE = "xpu:0"
    MEMORY_FRACTION = 0.8
    
    # Flask configuration
    HOST = "localhost"
    PORT = 5000
    DEBUG = False  # Disable auto-reload to prevent restarts during quiz/hint generation
    USE_RELOADER = False  # Explicitly disable reloader
    
    # Paths
    MODEL_CACHE_DIR = "./models_cache"
    
    @staticmethod
    def create_directories():
        os.makedirs(Config.MODEL_CACHE_DIR, exist_ok=True)
