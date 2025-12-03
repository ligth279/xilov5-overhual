# Xilo AI Tutor - Large v5 Overhaul

**Version 5.09.5** (Frontend + Lessons Release)

An advanced AI tutoring system with modular model architecture, powered by GPT-OSS 20B and Llama 3.1 8B, optimized for Intel Arc GPU with Vulkan acceleration.

> **Milestone Release**: Complete frontend rebuild with working lessons system, split-view interface, and AI-powered quiz flow.

## Branches

**main**: Stable production branch  
**v5.09.5**: Frontend + lessons system (current)
**v5.9-backend-only**: Backend-only branch (previous)
**latest**: Development branch

## 🚀 Features (v5.09.5)

### Core Features
- **Modular Model Architecture**: GPT-OSS 20B (reasoning model) with Llama 3.1 8B support
- **Vulkan GPU Acceleration**: llama.cpp with Vulkan backend for Intel Arc GPUs
- **Reasoning Model Support**: Automatic extraction of final answers from chain-of-thought models
- **Multilingual Support**: 13 languages (English + 12 Indian languages) with translation toggle

### Lesson System
- **3-Phase Learning Flow**: 
  1. **Explanation**: Read content with doubt chat available
  2. **Assessment**: Quiz with AI-powered hints
  3. **Completion**: Progress tracking and stats
- **Split-View Interface**: Content/quiz on left (60%), doubt chat on right (40%)
- **AI-Powered Hints**: Context-aware hints based on student's specific answer
- **Smart Quiz Closure**: Automatically closes quiz if answer is completely unrelated
- **Progress Tracking**: Resume lessons from last incomplete section (localStorage + backend)
- **Auto-Generated Hints**: No hint button - AI generates feedback immediately after wrong answers

### Answer Evaluation
- **3-Tier Hint System**:
  1. Spelling check (80% similarity) → "Check your spelling"
  2. AI categorization (related answer) → Contextual hint without revealing answer
  3. Unrelated answer → Close quiz, force material review
- **Max Attempts**: 3 attempts per question with adaptive feedback

### Frontend
- **Modern Light Theme**: Excellent readability, clean design
- **Responsive Design**: Works on desktop and mobile
- **Language Selector**: 13 languages with deep/AI translation toggle
- **Chat Interface**: Working chat page with message history
- **Lessons Grid**: Grade/subject filters with lesson cards
- **Split-View Modal**: Full-screen lesson viewer with doubt chat

## 🏗️ Architecture

- **Backend**: Flask + APIFlask with llama.cpp server integration
- **Frontend**: HTML5/CSS3/JavaScript with modal-based lesson viewer
- **AI Models** (Modular System): 
  - **GPT-OSS 20B** (Active): Reasoning model with chain-of-thought extraction
  - **Llama 3.1 8B Instruct** (Ready): Direct instruction-following model
  - **Mistral 7B** (Optional): Available for evaluation tasks
- **Hardware**: Intel Arc GPUs (B580 recommended: 12GB VRAM + 8GB shared = 20GB total)
- **Acceleration**: llama.cpp with Vulkan backend (GPU offloading)

## 📁 Project Structure

```
xilov5/
├── app.py                          # Main Flask application
├── models/                         # Model implementations
│   ├── gptoss_model.py            # GPT-OSS 20B (active)
│   ├── llama_model.py             # Llama 3.1 8B
│   └── mistral_model.py           # Mistral 7B
├── utils/                          # Utilities
│   ├── lesson_manager.py          # Lesson loading/management
│   ├── answer_evaluator.py        # 3-tier hint system
│   ├── chat_memory.py             # Conversation history
│   └── language_manager.py        # Multilingual support
├── templates/                      # HTML templates
│   ├── index.html                 # Chat page
│   └── lessons.html               # Lessons page (split-view)
├── static/                         # Frontend assets
│   ├── css/
│   │   ├── base.css               # Design system (light theme)
│   │   ├── chat.css               # Chat interface styles
│   │   └── lessons.css            # Lessons interface styles
│   └── js/
│       ├── chat.js                # Chat functionality
│       └── lessons.js             # Lessons functionality (500+ lines)
└── lessons/                        # Lesson content (JSON)
    ├── grade_5/
    │   ├── english/
    │   │   └── poetry_basics.json
    │   ├── math/
    │   └── science/
    └── metadata.json
```

## ⚠️ SYSTEM REQUIREMENTS

### ⚡ GPU Acceleration
**This software uses Vulkan for GPU acceleration. Intel Arc GPUs recommended, but any Vulkan-compatible GPU may work.**

### Hardware Requirements
- **Intel Arc GPU**: Battlemage B580 (12GB + 8GB shared = 20GB total) or A770 recommended
- **Vulkan Support**: Required for GPU acceleration  
- **GPU Memory**: 12-20GB total VRAM (for GPT-OSS 20B)
- **System RAM**: 16GB minimum (32GB recommended)
- **Storage**: 20GB free space (for model files)

### Software Requirements
- **Operating System**: Windows 10/11 (64-bit)
- **Python**: 3.11 recommended (3.8-3.11 supported)
- **Intel GPU Drivers**: Latest version from Intel
- **llama.cpp**: Installed via winget (ggml.llamacpp)
- **Vulkan Runtime**: Included with llama.cpp from winget

### Compatibility Notes
- **Intel Arc GPU**: Fully supported with Vulkan backend
- **NVIDIA GPUs**: May work with Vulkan (not tested)
- **AMD GPUs**: May work with Vulkan (not tested)
- **Intel Integrated Graphics**: Not recommended (insufficient VRAM)
- **CPU-only execution**: Possible but extremely slow (~0.5 tok/s)

## 🛠️ Installation

### Prerequisites
```powershell
# 1. Install Intel GPU drivers (latest from Intel website)

# 2. Install llama.cpp with Vulkan support via winget
winget install ggml.llamacpp

# 3. Verify llama-server.exe is installed
$env:LOCALAPPDATA + "\Microsoft\WinGet\Packages\ggml.llamacpp_Microsoft.Winget.Source_8wekyb3d8bbwe\llama-server.exe"
```

### Dependencies
```bash
# Install Python dependencies
pip install flask apiflask requests deep_translator

# Optional: For debugging/monitoring
pip install psutil
```

### Model Setup
**GPT-OSS 20B** (Current):
- Download via AI Playground or manually from HuggingFace
- Default location: `C:\Users\{user}\AppData\Local\Programs\AI Playground\resources\service\models\llm\ggufLLM\unsloth---gpt-oss-20b-GGUF\gpt-oss-20b-Q8_0.gguf`
- Size: ~13.9GB

**Llama 3.1 8B** (Alternative):
- Download GGUF from HuggingFace: `bartowski/Meta-Llama-3.1-8B-Instruct-GGUF`
- Update path in `models/llama31_model.py` line 31
- Size: ~8.5GB (Q8_0)

## 🚀 Usage

### Starting the Server
```bash
python app.py
```

### Accessing the Interface
Open your browser and navigate to:
```
http://localhost:5000
```

### Features
- **Lesson Browser**: Browse lessons by grade (5-12) and subject
- **3-Phase Learning**: 
  1. Explanation with reading material
  2. Doubt clearing chat (multilingual, 13 languages)
  3. Assessment with AI-powered hints
- **Progress Tracking**: Automatic progress saving per user
- **Answer Evaluation**: GPT-OSS 20B provides reasoning-based feedback and hints
- **Reasoning Model Support**: Automatic extraction of final answers from chain-of-thought

## 📊 Performance Metrics

### Intel Arc B580 Performance (GPT-OSS 20B + Vulkan)
- **Model Loading**: 48-60 seconds (13.9GB model)
- **VRAM Usage**: 13.9GB (GPT-OSS 20B)
- **Generation Speed**: 3.7-7.0 tok/s (varies with context length)
- **Chat Response**: 18-48 seconds (depending on complexity)
- **Hint Generation**: 15-30 seconds (shorter prompts)
- **Concurrent Users**: Single user (exclusive GPU usage)

### Optimization Features
- Q8_0 quantization (8-bit)
- Vulkan GPU offloading (all layers)
- 120-second timeout for long responses
- Reasoning chain extraction (marker-based)
- Conversation history (last 3 exchanges)
- Rule-based spelling check (80% similarity)

## 🔧 Technical Details

### Model Configuration

**GPT-OSS 20B** (Active):
```python
Model Type: Reasoning model (chain-of-thought)
Generation Parameters:
- max_new_tokens: 512-800 (educational responses)
- temperature: 0.7 (balanced creativity)
- top_p: 0.9
- Reasoning marker: <|start|>assistant<|channel|>final<|message|
- Context: 2048 tokens
- Stop sequences: ["User:", "\nUser:", "Human:", "\nHuman:"]
```

**Llama 3.1 8B Instruct** (Ready for deployment):
```python
Model Type: Direct instruction-following
Generation Parameters:
- max_new_tokens: 512
- temperature: 0.7
- top_p: 0.9
- Chat template: Llama 3 format (<|begin_of_text|>, <|eot_id|>)
- Context: 4096 tokens (supports up to 128K)
- Stop sequences: ["<|eot_id|>", "<|end_of_text|>"]
```

### Answer Evaluation Flow
1. **Spelling Check** (Rule-based): 80%+ similarity → spelling hint
2. **AI Categorization** (GPT-OSS 20B): Related vs Unrelated
3. **Related**: Explain difference + give pedagogical clue
4. **Unrelated**: Close quiz, return to reading

## 📁 Project Structure

```
xilov5/
├── app.py                     # Flask API server (main application)
├── config.py                  # Configuration (v5.09.00)
├── models/
│   ├── gptoss_model.py        # GPT-OSS 20B wrapper (Vulkan + reasoning extraction)
│   ├── llama31_model.py       # Llama 3.1 8B wrapper (ready for deployment)
│   ├── phi_model.py           # Phi 3.5 (deactivated - IPEX-LLM issues)
│   └── mistral_7b.py          # Mistral 7B (deactivated - IPEX-LLM issues)
├── utils/
│   ├── intel_gpu.py          # Intel XPU utilities
│   ├── answer_evaluator.py  # Answer evaluation + hints
│   ├── lesson_manager.py    # Lesson loading/querying
│   ├── progress_tracker.py  # Student progress tracking
│   └── language_support.py  # Multilingual support (13 languages)
├── lessons/                   # Lesson JSON files
│   └── grade_X/subject/
├── user_progress/             # Student progress files
├── static/
│   ├── css/
│   │   └── lessons.css       # Lesson UI styling
│   └── js/
│       └── lessons.js        # Lesson frontend logic
├── templates/
│   ├── index.html            # Landing page
│   └── lessons.html          # Lesson viewer
└── README.md                 # This file
```

## 🐛 Troubleshooting

### Common Issues

**Models not loading:**
```bash
# Check if both models are cached
ls ~/.cache/huggingface/hub/
```

**High VRAM usage:**
- Both models use ~10-14 GB total
- Close other GPU applications
- Ensure 4-bit quantization is enabled

**Inaccurate hints:**
- Mistral 7B should handle evaluation (check logs)
- Verify Mistral loaded successfully
- Check temperature settings (should be 0.1)

**Quiz not closing on wrong answers:**
- Check backend logs for "should_retry_section" flag
- Verify trigger phrase detection in app.py

## 📈 Version History

### v5.09.00 - Final v5 Release (Model Architecture Overhaul)
- ✅ Integrated GPT-OSS 20B reasoning model with marker-based answer extraction
- ✅ Added Llama 3.1 8B Instruct support (modular design)
- ✅ Implemented reasoning chain extraction (`<|start|>assistant<|channel|>final<|message|>` marker)
- ✅ Migrated from IPEX-LLM to llama.cpp + Vulkan for stability
- ✅ Deactivated Phi 3.5 Mini and Mistral 7B (IPEX-LLM compatibility issues)
- ✅ Disabled Flask auto-reload to prevent model operation interruptions
- ✅ Updated prompt engineering for reasoning models
- ✅ Fixed timeout issues (60s → 120s for long responses)
- ✅ Modular model architecture for easy model swapping
- 📝 Last major release before v6 architectural redesign

### v5.02.00 - Dual-Model System
- ✅ Added Mistral 7B for answer evaluation
- ✅ Dual-model architecture (Phi chat + Mistral evaluation)
- ✅ Improved hint accuracy and consistency
- ✅ Rule-based spelling check (80% similarity)
- ✅ Auto-close quiz on unrelated answers

### v5.01.00 - Lesson System
- ✅ 3-phase lesson flow
- ✅ Multilingual doubt chat (13 languages)
- ✅ Progress tracking system
- ✅ AI-powered hints
- ✅ Split-view interface

### v5.00.00 - Initial Release
- ✅ Intel XPU optimization
- ✅ Phi 3.5 Mini integration
- ✅ Web interface
- ✅ Intel Arc B580 support

## 🔒 License & Copyright

**Copyright © 2025 Joseph-Babu**

**All Rights Reserved**

This software is proprietary and confidential. This software is licensed for **personal use only**. 

**Restrictions:**
- No commercial use permitted
- No redistribution allowed
- No modification for commercial purposes
- No open source licensing

**Personal Use License:**
- You may use this software for personal, non-commercial purposes with permission from the author
- You may modify the software for your own personal use
- You may not distribute, share, or sell this software or any derivatives

For licensing inquiries, commercial use requests, or personal use permission, please contact the author.

## 👨‍💻 Author

**Joseph**
- Lead Developer
- AI/ML Developer  
- Intel XPU Expert

---

## 🙏 Acknowledgments

- **OpenAI** for the GPT-OSS open-weight reasoning models
- **Meta** for the Llama 3.1 model family
- **Intel GPU Team** for XPU acceleration technology and Arc GPU development
- **Intel AI Playground Team** for AI Playground and model distribution infrastructure
- **ggerganov** and the llama.cpp community for efficient local inference
- Microsoft for the Phi 3.5 model family (v5.0-5.2)
- Mistral AI for Mistral 7B models (v5.1-5.2)
- PyTorch team for XPU integration
- Hugging Face for model hosting and Transformers library

---

**Xilo AI Tutor v5.09.00** - Powered by Intel Arc GPU (Vulkan) & llama.cpp
