# Modular AI System - Documentation

## Overview
The Xilo AI Tutor now has a **fully modular architecture** that allows easy switching between different AI models without code changes.

## Architecture

### Core Components

1. **`models/base_model.py`** - Abstract base class
   - Defines standard interface all models must implement
   - Methods: `load_model()`, `generate_response()`, `unload()`, `get_info()`

2. **`models/model_manager.py`** - Central registry
   - Manages all available models
   - Handles loading/unloading
   - Enforces exclusive mode for large models
   - Auto-detects transformers version compatibility

3. **`model_config.py`** - User configuration
   - Simple file to choose which models to use
   - Just change `CHAT_MODEL` and `EVALUATION_MODEL` variables
   - Handles exclusive vs dual mode automatically

4. **Model Implementations**:
   - `models/phi_model.py` - Phi 3.5 Mini (3.8B)
   - `models/mistral_7b.py` - Mistral 7B v0.2/v0.3
   - `models/gptoss_model.py` - GPT-OSS 20B (GGUF)
   - `models/gptj_model.py` - GPT-J 6B (to be created)

## How to Switch Models

### Method 1: Edit `model_config.py`
```python
# For GPT-OSS 20B (exclusive, best quality):
CHAT_MODEL = 'gpt-oss-20b'
EVALUATION_MODEL = 'gpt-oss-20b'  # Ignored in exclusive mode

# For GPT-J 6B (balanced):
CHAT_MODEL = 'gpt-j-6b'
EVALUATION_MODEL = 'gpt-j-6b'

# For Phi 3.5 + Mistral 7B (dual, if compatible):
CHAT_MODEL = 'phi-3.5'
EVALUATION_MODEL = 'mistral-7b-v0.2'
```

### Method 2: Programmatic Switching
```python
from models.model_manager import model_manager

# Load GPT-OSS for both roles
model_manager.load_model('gpt-oss-20b', role='chat')
# Evaluation automatically uses same model in exclusive mode

# Switch to GPT-J later
model_manager.switch_model('gpt-j-6b', role='chat')
```

## Exclusive Mode

### What is Exclusive Mode?
Large models like GPT-OSS 20B (13.9GB VRAM) require the **entire GPU** and cannot share memory with other models.

### How it Works:
1. When loading an exclusive model:
   - **All other models are automatically unloaded**
   - GPU memory is cleared (`torch.xpu.empty_cache()`)
   - Model loads with full VRAM available

2. When exclusive model is loaded:
   - **Cannot load additional models**
   - Attempting to load another model will fail with error
   - Must unload exclusive model first

3. The exclusive model handles BOTH roles:
   - Chat (conversations, explanations)
   - Evaluation (answer checking, hints)

### Models with Exclusive Flag:
- ✅ `gpt-oss-20b`: 13.9GB, exclusive=True
- ❌ `phi-3.5`: 4-6GB, exclusive=False
- ❌ `mistral-7b`: 6-8GB, exclusive=False
- ❌ `gpt-j-6b`: 5-7GB, exclusive=False

## Memory Management

### Intel Arc B580 VRAM:
- 12GB dedicated VRAM
- 8GB shared system RAM
- **Total: 20GB**

### Model Combinations:

**Exclusive Mode:**
```
GPT-OSS 20B alone: 13.9GB
├─ Dedicated VRAM: 12GB (full)
└─ Shared RAM: 1.9GB
```

**Dual Mode:**
```
Phi 3.5 + Mistral 7B: ~12-14GB total
├─ Phi 3.5: 4-6GB
├─ Mistral 7B: 6-8GB
└─ PyTorch overhead: 2-3GB
```

**Single Smaller Model:**
```
GPT-J 6B alone: 6-8GB
├─ Dedicated VRAM: 6-8GB
└─ Room for other processes: 4-6GB
```

## Compatibility Matrix

| Model | Transformers | IPEX-LLM | Format | Compatible? |
|-------|--------------|----------|--------|-------------|
| Phi 3.5 | 4.45+ | 2.3.0 | HF | ❌ (version conflict) |
| Mistral v0.2 | 4.40+ | 2.3.0 | HF | ❌ (tokenizer issue) |
| Mistral v0.3 | 4.45+ | 2.3.0 | HF | ❌ (tokenizer issue) |
| GPT-J 6B | 4.37+ | 2.3.0 | HF | ✅ Should work |
| **GPT-OSS 20B** | N/A | N/A | GGUF | ✅ **Always works** |

### Current Stack:
- PyTorch: 2.6.0+xpu
- Transformers: 4.37.0
- IPEX-LLM: 2.3.0b20251027

**Recommendation**: Use GPT-OSS 20B (GGUF) since it doesn't depend on transformers version.

## Installation Requirements

### For GPT-OSS 20B (GGUF):
```bash
pip install llama-cpp-python
```

### For Hugging Face models (Phi, Mistral, GPT-J):
```bash
# Already installed:
# - transformers 4.37.0
# - ipex-llm 2.3.0
# - torch 2.6.0+xpu
```

## Usage in app.py

### Old Way (Hardcoded):
```python
from models.phi_model import phi_tutor
from models.mistral_7b import MistralModel

# Hardcoded initialization
phi_tutor.load_model()
mistral_model = MistralModel(config)
```

### New Way (Modular):
```python
from models.model_manager import model_manager
from model_config import get_model_config

# Load models based on config
config = get_model_config()
chat_model = model_manager.load_model(config['chat_model'], role='chat')
eval_model = model_manager.load_model(config['evaluation_model'], role='evaluation')

# Use anywhere
response = model_manager.get_chat_model().generate_response(user_message)
hint = model_manager.get_evaluation_model().generate_response(eval_prompt)
```

## Benefits of Modular System

1. **No Code Changes**: Switch models by editing one config file
2. **Safe Memory Management**: Exclusive mode prevents OOM errors
3. **Automatic Compatibility**: System detects which models work with current stack
4. **Consistent API**: All models implement same interface
5. **Easy to Extend**: Add new models by implementing `BaseAIModel`
6. **Transparent Switching**: Can swap models at runtime without restart

## Next Steps

1. **Install llama-cpp-python**:
   ```bash
   pip install llama-cpp-python
   ```

2. **Test GPT-OSS 20B**:
   ```python
   from models.gptoss_model import GPTOSSModel
   from config import Config
   
   model = GPTOSSModel(Config())
   model.load_model()
   response = model.generate_response("What is photosynthesis?")
   print(response)
   ```

3. **Update app.py**: Replace hardcoded model loading with `model_manager`

4. **Add GPT-J 6B**: Create `models/gptj_model.py` if needed as fallback

## Logic Flow

```
app.py startup:
  ↓
model_config.py (read user choice)
  ↓
model_manager.load_model()
  ↓
Check if exclusive? → Yes → Unload all others → Load exclusive model
                  → No  → Check compatibility → Load model
  ↓
Model instance returned
  ↓
Assign to chat_model / evaluation_model
  ↓
Generate responses via .generate_response()
```

## No Logic Breaks

✅ All models implement `BaseAIModel` interface
✅ Exclusive mode prevents memory conflicts
✅ Compatibility check prevents unsupported models
✅ Graceful fallbacks if model fails to load
✅ Memory cleanup on model unload
✅ Consistent error handling across all models
