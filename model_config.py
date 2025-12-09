"""
Model Configuration - Choose which models to use
Edit this file to switch between different AI models
"""

# =============================================================================
# MODEL SELECTION
# =============================================================================

# Choose your chat model (handles conversations, explanations)
# Options:
#   - 'gpt-oss-20b': Large GGUF model, 13.9GB VRAM, best quality (EXCLUSIVE)
#   - 'gpt-j-6b': Medium model, 5-7GB VRAM, good balance
#   - 'phi-3.5': Small model, 4-6GB VRAM, fast (requires transformers 4.45+)
CHAT_MODEL = 'gpt-oss-20b'

# Choose your evaluation model (handles answer checking, hints)
# Options: Same as chat model
# Note: If using 'gpt-oss-20b', it handles BOTH chat and evaluation (exclusive mode)
EVALUATION_MODEL = 'gpt-oss-20b'  # Will be ignored if CHAT_MODEL is exclusive

# =============================================================================
# EXCLUSIVE MODE BEHAVIOR
# =============================================================================
# When using GPT-OSS 20B:
#   - It runs ALONE (13.9GB VRAM)
#   - Handles both chat and evaluation
#   - All other models are automatically unloaded
#   - Best quality but uses most memory

# When using smaller models (GPT-J, Phi, Mistral):
#   - Can run multiple models simultaneously
#   - Chat model + Evaluation model (dual setup)
#   - More memory efficient but may need more total VRAM

# =============================================================================
# VRAM USAGE GUIDE
# =============================================================================
# Your Intel Arc B580: 12GB dedicated + 8GB shared = 20GB total
#
# Single Model (Exclusive):
#   - GPT-OSS 20B: 13.9GB (uses shared RAM too)
#
# Dual Model Setup:
#   - Phi 3.5 (chat) + Mistral 7B (eval): ~12-14GB total
#   - GPT-J 6B (both): ~6-8GB (can run alone)
#
# Recommendation:
#   - For best quality: GPT-OSS 20B (exclusive)
#   - For balanced: GPT-J 6B (both roles)
#   - For speed: Phi 3.5 + smaller eval model (if transformers 4.45+ available)

# =============================================================================
# AUTO-CONFIGURATION
# =============================================================================
def get_model_config():
    """
    Returns the active model configuration.
    Automatically handles exclusive mode.
    """
    from models.model_manager import model_manager
    
    # Get model info
    chat_info = model_manager.AVAILABLE_MODELS.get(CHAT_MODEL, {})
    eval_info = model_manager.AVAILABLE_MODELS.get(EVALUATION_MODEL, {})
    
    # Check if chat model is exclusive
    if chat_info.get('exclusive', False):
        return {
            'mode': 'exclusive',
            'chat_model': CHAT_MODEL,
            'evaluation_model': CHAT_MODEL,  # Same model for both
            'note': f"{chat_info['display_name']} handles everything"
        }
    else:
        return {
            'mode': 'dual',
            'chat_model': CHAT_MODEL,
            'evaluation_model': EVALUATION_MODEL,
            'note': 'Separate models for chat and evaluation'
        }
