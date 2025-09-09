import os

class Config:
    # Model configuration
    MODEL_NAME = "microsoft/Phi-3.5-mini-instruct"
    MAX_LENGTH = 2048
    TEMPERATURE = 0.7
    TOP_P = 0.9
    
    # Intel GPU configuration
    USE_XPU = True
    XPU_DEVICE = "xpu:0"
    MEMORY_FRACTION = 0.8
    
    # Flask configuration
    HOST = "localhost"
    PORT = 5000
    DEBUG = True
    
    # Paths
    MODEL_CACHE_DIR = "./models_cache"
    
    @staticmethod
    def create_directories():
        os.makedirs(Config.MODEL_CACHE_DIR, exist_ok=True)
