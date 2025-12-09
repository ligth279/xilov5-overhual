"""
Model Manager - Central registry for all AI models
Handles model selection, initialization, and switching
"""
import logging
from typing import Dict, Optional
from config import Config

logger = logging.getLogger(__name__)


class ModelManager:
    """
    Centralized model management system.
    Allows easy switching between different AI models without code changes.
    """
    
    # Model registry: maps model names to their class constructors
    AVAILABLE_MODELS = {
        'phi-3.5': {
            'class': 'models.phi_model.PhiTutor',
            'display_name': 'Phi 3.5 Mini (3.8B)',
            'use_case': 'chat',
            'transformers_version': '4.45+',
            'vram': '4-6GB',
            'exclusive': False,
            'compatible': False  # Set based on transformers version
        },
        'mistral-7b-v0.2': {
            'class': 'models.mistral_7b.MistralModel',
            'display_name': 'Mistral 7B v0.2',
            'use_case': 'evaluation',
            'transformers_version': '4.40+',
            'vram': '6-8GB',
            'exclusive': False,
            'compatible': False
        },
        'mistral-7b-v0.3': {
            'class': 'models.mistral_7b.MistralModel',
            'display_name': 'Mistral 7B v0.3',
            'use_case': 'evaluation',
            'transformers_version': '4.45+',
            'vram': '6-8GB',
            'exclusive': False,
            'compatible': False
        },
        'gpt-j-6b': {
            'class': 'models.gptj_model.GPTJModel',
            'display_name': 'GPT-J 6B',
            'use_case': 'both',
            'transformers_version': '4.37+',
            'vram': '5-7GB',
            'exclusive': False,
            'compatible': True  # Should work with current stack
        },
        'gpt-oss-20b': {
            'class': 'models.gptoss_model.GPTOSSModel',
            'display_name': 'GPT-OSS 20B (GGUF)',
            'use_case': 'both',
            'transformers_version': 'N/A',  # Uses llama.cpp, not transformers
            'vram': '13.9GB',
            'exclusive': True,  # ⚠️ Requires exclusive GPU usage
            'compatible': True,  # Always compatible (doesn't use transformers)
            'format': 'GGUF'
        }
    }
    
    def __init__(self):
        """Initialize model manager"""
        self.config = Config()
        self.chat_model = None
        self.evaluation_model = None
        self.loaded_models: Dict[str, any] = {}
        
        # Detect transformers version
        self._detect_compatibility()
    
    def _detect_compatibility(self):
        """Check which models are compatible with current transformers version"""
        try:
            import transformers
            version = transformers.__version__
            logger.info(f"Transformers version: {version}")
            
            # Parse version (e.g., "4.37.0" -> 4.37)
            major_minor = float('.'.join(version.split('.')[:2]))
            
            # Update compatibility flags
            for model_key, model_info in self.AVAILABLE_MODELS.items():
                required = model_info['transformers_version']
                if '+' in required:
                    min_version = float(required.replace('+', ''))
                    model_info['compatible'] = major_minor >= min_version
                else:
                    model_info['compatible'] = version.startswith(required)
            
            logger.info("Model compatibility check complete")
            
        except Exception as e:
            logger.error(f"Failed to detect transformers version: {e}")
    
    def get_available_models(self, use_case: Optional[str] = None):
        """
        Get list of available models.
        
        Args:
            use_case: Filter by use case ('chat', 'evaluation', 'both', or None for all)
            
        Returns:
            Dict of compatible models
        """
        available = {}
        for key, info in self.AVAILABLE_MODELS.items():
            if not info['compatible']:
                continue
            if use_case and info['use_case'] != use_case and info['use_case'] != 'both':
                continue
            available[key] = info
        
        return available
    
    def load_model(self, model_key: str, role: str = 'chat'):
        """
        Load a model by key.
        
        Args:
            model_key: Key from AVAILABLE_MODELS
            role: 'chat' or 'evaluation'
            
        Returns:
            Loaded model instance or None
        """
        if model_key not in self.AVAILABLE_MODELS:
            logger.error(f"Unknown model: {model_key}")
            return None
        
        model_info = self.AVAILABLE_MODELS[model_key]
        
        if not model_info['compatible']:
            logger.error(f"Model {model_key} not compatible with current transformers version")
            return None
        
        # ⚠️ EXCLUSIVE MODEL CHECK
        if model_info.get('exclusive', False):
            logger.warning(f"⚠️ {model_info['display_name']} requires exclusive GPU usage!")
            logger.warning(f"   VRAM required: {model_info['vram']}")
            
            # Unload ALL other models first
            if self.loaded_models:
                logger.info("Unloading all other models for exclusive model...")
                for key, instance in list(self.loaded_models.items()):
                    if key != model_key:
                        logger.info(f"  Unloading {key}...")
                        instance.unload()
                        del self.loaded_models[key]
                
                self.chat_model = None
                self.evaluation_model = None
                
                # Force garbage collection
                import gc
                gc.collect()
                try:
                    import torch
                    if torch.xpu.is_available():
                        torch.xpu.empty_cache()
                except:
                    pass
                
                logger.info("✅ GPU memory cleared for exclusive model")
        
        # Check if already loaded
        if model_key in self.loaded_models:
            logger.info(f"Model {model_key} already loaded")
            return self.loaded_models[model_key]
        
        # REVERSE CHECK: Don't allow non-exclusive models if exclusive model is loaded
        exclusive_loaded = any(
            self.AVAILABLE_MODELS[key].get('exclusive', False) 
            for key in self.loaded_models.keys()
        )
        if exclusive_loaded and not model_info.get('exclusive', False):
            logger.error(f"Cannot load {model_key}: Exclusive model already loaded")
            logger.error(f"Unload exclusive model first!")
            return None
        
        try:
            # Dynamic import
            module_path, class_name = model_info['class'].rsplit('.', 1)
            module = __import__(module_path, fromlist=[class_name])
            ModelClass = getattr(module, class_name)
            
            # Instantiate and load
            logger.info(f"Loading {model_info['display_name']}...")
            model_instance = ModelClass(self.config)
            
            # Models with __init__ that auto-loads won't need explicit load_model()
            if not model_instance.is_loaded and hasattr(model_instance, 'load_model'):
                model_instance.load_model()
            
            # Cache the loaded model
            self.loaded_models[model_key] = model_instance
            
            # Assign to role
            if role == 'chat':
                self.chat_model = model_instance
            elif role == 'evaluation':
                self.evaluation_model = model_instance
            
            logger.info(f"✅ {model_info['display_name']} loaded for {role}")
            return model_instance
            
        except Exception as e:
            logger.error(f"Failed to load {model_key}: {e}")
            return None
    
    def switch_model(self, model_key: str, role: str = 'chat'):
        """
        Switch to a different model for a given role.
        Unloads current model if specified.
        
        Args:
            model_key: New model to load
            role: 'chat' or 'evaluation'
            
        Returns:
            bool: Success status
        """
        # Unload current model for this role
        current_model = self.chat_model if role == 'chat' else self.evaluation_model
        if current_model:
            logger.info(f"Unloading current {role} model: {current_model.model_name}")
            current_model.unload()
        
        # Load new model
        new_model = self.load_model(model_key, role)
        return new_model is not None
    
    def get_chat_model(self):
        """Get active chat model"""
        return self.chat_model
    
    def get_evaluation_model(self):
        """Get active evaluation model"""
        return self.evaluation_model
    
    def unload_all(self):
        """Unload all models and free memory"""
        for model_key, model_instance in self.loaded_models.items():
            logger.info(f"Unloading {model_key}...")
            model_instance.unload()
        
        self.loaded_models.clear()
        self.chat_model = None
        self.evaluation_model = None
        logger.info("All models unloaded")
    
    def get_status(self):
        """Get current model status"""
        return {
            'chat_model': self.chat_model.get_info() if self.chat_model else None,
            'evaluation_model': self.evaluation_model.get_info() if self.evaluation_model else None,
            'loaded_models': list(self.loaded_models.keys()),
            'available_models': self.get_available_models()
        }


# Global model manager instance
model_manager = ModelManager()
