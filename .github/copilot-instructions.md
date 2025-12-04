## Xilo AI Tutor Project

This project is an AI tutor website with dual-model architecture optimized for Intel GPU with XMX engines.

### Key Features:
- Intel Arc GPU optimization with Vulkan (llama.cpp)
- Single unified model architecture (user chooses at startup)
- Web-based interface with lesson system
- GGUF quantized models (Q4_K_S to Q8_0)

### Architecture:
- **Backend**: Flask with llama.cpp + Vulkan GPU acceleration
- **Frontend**: HTML/CSS/JavaScript with split-view lesson interface
- **Models** (choose one via `--model` flag):
  - **GPT-OSS 20B** (Q8_0, 11.28GB): Reasoning model with chain-of-thought (default)
  - **Llama 3.1 8B** (Q5_K_S, 5.21GB): Fast direct responses
  - **Mistral 7B** (Q4_K_S, 3.86GB): Lightweight instruction-following
- **Hardware**: Intel Arc B580 (12GB dedicated + 8GB shared = 20GB total)

### Model Architecture (v5.09.5):

**Single Unified Model System:**
- User chooses ONE model at startup: `python app.py --model gptoss|llama31|mistral`
- Selected model handles ALL tasks:
  - General chat / doubt clearing
  - Answer evaluation
  - Hint generation
  
**Model Details:**

#### GPT-OSS 20B (Default - Reasoning Model)
- **File**: `gpt-oss-20b-Q8_0.gguf` (11.28 GB)
- **Backend**: llama.cpp with Vulkan
- **Performance**: 4-7 tok/s on Intel Arc B580
- **VRAM**: 13.9GB during generation
- **Capabilities**: 
  - Chain-of-thought reasoning (shows internal thinking)
  - Extracts final answer from reasoning
  - Best for complex problem-solving
- **Conversation History**: None (stateless by default)
- **Format**: Native GPT-OSS tags (`<|start|>assistant<|channel|>final<|message|>`)

#### Llama 3.1 8B (Fast Direct Model)
- **File**: `Meta-Llama-3.1-8B-Instruct-Q5_K_S.gguf` (5.21 GB)
- **Backend**: llama.cpp with Vulkan
- **Performance**: 6-10 tok/s on Intel Arc B580
- **VRAM**: 8-9GB during generation
- **Capabilities**: 
  - Direct answers (no reasoning chains)
  - Good for general tutoring
  - Fast responses
- **Conversation History**: Optional (can store last 3 exchanges)
- **Format**: Llama 3 chat template (auto-detected from GGUF)

#### Mistral 7B (Lightweight Model)
- **File**: `Mistral-7B-Instruct-v0.3-Q4_K_S.gguf` (3.86 GB)
- **Backend**: llama.cpp with Vulkan
- **Performance**: 8-12 tok/s on Intel Arc B580
- **VRAM**: 4-5GB during generation
- **Capabilities**: 
  - Lightweight instruction-following
  - Fastest inference
  - Good for simple Q&A
- **Conversation History**: Optional (can store last 3 exchanges)
- **Format**: Mistral Instruct tags (`[INST] ... [/INST]`)

**Key Differences from v5.08:**
- ❌ No more dual-model system (Phi + Mistral)
- ❌ No more PyTorch/IPEX-LLM
- ❌ No more model offloading between CPU/GPU
- ✅ Single model instance per session (simpler, more stable)
- ✅ llama.cpp with Vulkan (more compatible, easier setup)
- ✅ User chooses model based on needs (speed vs quality)

### Setup Requirements (v5.09.5):
- Intel Arc GPU (B580 with 12GB+ VRAM recommended)
- llama.cpp with Vulkan support (installed via WinGet)
- Python 3.11+ with Flask
- GGUF model files (downloaded from AI Playground or HuggingFace)

### Project Status (v5.09.5):
✅ Project structure created
✅ llama.cpp with Vulkan backend integrated
✅ Single unified model system (user selects at startup)
✅ Web interface fully functional
✅ 3-phase lesson flow (Explanation → Doubt Clearing → Assessment)
✅ Multilingual support (13 languages)
✅ AI-powered hints with spell check
✅ Progress tracking system (sessionStorage - tab-scoped)
✅ Git branch v5.09.5 pushed to GitHub
🚀 **Xilo AI Tutor running at http://localhost:5000**

### Current Architecture:
- **Backend**: Flask + llama.cpp server (subprocess)
- **Model Loading**: One model at a time (gptoss OR llama31 OR mistral)
- **Processing**: Sequential (one request at a time)
- **VRAM**: Single model instance (no offloading needed)
- **Conversation**: Optional history (last 3 exchanges for context)
### Known Issues & Solutions (v5.09.5):
- ✅ **llama.cpp Vulkan backend** - Stable, no memory leaks
- ✅ **Single model architecture** - No offloading complexity
- ✅ **GGUF quantization** - Optimized for memory efficiency
- ⚠️ **Sequential processing** - One request at a time (queue needed for multiple users)
- 🔧 **GPT-OSS reasoning extraction** - Not yet implemented (strips reasoning by default)

### Answer Evaluation Flow:
1. **Spelling Check** (Rule-based): 80%+ character similarity → "Check your spelling"
2. **AI Categorization** (Unified Model): Related vs Unrelated
3. **Related**: Explain their answer + give clue (no reveal)
4. **Unrelated**: "That's not related to the topic. Please review the material and try again." → Close quiz

### Development Notes (v5.09.5):
- One model instance at a time (gptoss OR llama31 OR mistral)
- No model offloading needed (single model)
- VRAM usage: 4-14GB depending on model choice
- Can run on Intel Arc B580 (12GB dedicated + 8GB shared = 20GB total)
- All models support optional conversation history (last 3 exchanges)
- Progress tracking uses sessionStorage (tab-scoped, resets on close)