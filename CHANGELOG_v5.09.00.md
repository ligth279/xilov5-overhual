# Xilo AI Tutor - Version 5.09.00 Release Notes

**Release Date**: December 2, 2025  
**Version**: 5.09.00 (Final v5 Release)  
**Codename**: Model Architecture Overhaul

---

## 🎯 Overview

This is the **final major release** of Xilo AI Tutor version 5 before the v6 architectural redesign. Version 5.09.00 represents a complete overhaul of the model architecture, migrating from IPEX-LLM to llama.cpp with Vulkan backend for improved stability and performance.

---

## ✨ Major Changes

### 🤖 New AI Models

**Active Models:**
- ✅ **GPT-OSS 20B** (Primary)
  - OpenAI's open-weight reasoning model
  - 13.9GB VRAM usage
  - Chain-of-thought with automatic answer extraction
  - Marker-based reasoning separation: `<|start|>assistant<|channel|>final<|message|>`

- ✅ **Llama 3.1 8B Instruct** (Ready for deployment)
  - Meta's instruction-following model
  - 8-9GB VRAM usage
  - Direct responses without reasoning chains
  - Modular integration ready

**Deactivated Models:**
- ❌ Phi 3.5 Mini (3.8B) - IPEX-LLM compatibility issues
- ❌ Mistral 7B v0.2 - IPEX-LLM compatibility issues
- ❌ Mistral 7B v0.3 - IPEX-LLM compatibility issues

### 🏗️ Architecture Changes

1. **Inference Backend Migration**
   - ❌ Old: IPEX-LLM + PyTorch XPU
   - ✅ New: llama.cpp + Vulkan GPU acceleration
   - **Why**: IPEX-LLM had persistent DLL issues and transformers compatibility problems

2. **Modular Model System**
   - Each model in separate file (`gptoss_model.py`, `llama31_model.py`)
   - Class-level configuration flags (`IS_REASONING_MODEL`, `REASONING_MARKER`)
   - Easy model swapping via imports

3. **Reasoning Model Support**
   - Automatic detection of reasoning vs direct-response models
   - Marker-based answer extraction (GPT-OSS)
   - Pattern-based fallback extraction
   - Clean separation of thinking process from final answer

### 🔧 Technical Improvements

1. **Timeout Handling**
   - Increased from 60s → 120s for long responses
   - Fixes timeout errors during example generation
   - Allows completion of mathematical explanations

2. **Stop Sequences**
   - Removed problematic `\n\n\n` stop token
   - Now only stops on conversation turn markers
   - Prevents premature cutoff of formatted responses

3. **Conversation History**
   - Properly integrated into prompt building
   - Last 3 exchanges maintained for context
   - Works with both reasoning and non-reasoning models

4. **Flask Auto-Reload**
   - Disabled (`DEBUG = False`, `use_reloader=False`)
   - Prevents server restarts during model operations
   - Stops watchdog from detecting library file changes

5. **Prompt Engineering**
   - Anti-reasoning system prompts for non-reasoning contexts
   - Reasoning extraction instructions for GPT-OSS
   - Grade-appropriate response length guidelines

### 📦 Installation Changes

**New Dependencies:**
```bash
# Install llama.cpp with Vulkan via winget
winget install ggml.llamacpp

# No longer needed:
# - ipex-llm
# - intel-extension-for-pytorch
# - transformers (for model loading)
```

**Model Files:**
- GPT-OSS 20B: `C:\Users\{user}\AppData\Local\Programs\AI Playground\resources\service\models\llm\ggufLLM\unsloth---gpt-oss-20b-GGUF\gpt-oss-20b-Q8_0.gguf`
- Llama 3.1 8B: Manual download from HuggingFace (GGUF format)

---

## 🐛 Bug Fixes

1. **Reasoning Leak Fixed**
   - Issue: GPT-OSS outputting internal reasoning process
   - Fix: Marker-based extraction + pattern fallback
   - Result: Users only see final answers

2. **Response Cutoff Fixed**
   - Issue: Responses truncating mid-sentence
   - Fix: Removed `\n\n\n` stop sequence
   - Result: Complete mathematical explanations

3. **Timeout Errors Fixed**
   - Issue: Long examples timing out at 60s
   - Fix: Increased timeout to 120s
   - Result: Example generation completes successfully

4. **Auto-Reload Interruptions Fixed**
   - Issue: Server restarting during quiz/hint operations
   - Fix: Disabled Flask auto-reload
   - Result: Stable operation during student interactions

---

## 📊 Performance Metrics

### GPT-OSS 20B (Vulkan)
- **Load Time**: 48-60 seconds
- **VRAM Usage**: 13.9GB
- **Generation Speed**: 3.7-7.0 tok/s (varies with prompt length)
- **Context Window**: 2048 tokens
- **Quantization**: Q8_0 (8-bit)

### Llama 3.1 8B (Vulkan) - Estimated
- **Load Time**: ~30-40 seconds
- **VRAM Usage**: 8-9GB
- **Generation Speed**: 6-10 tok/s (estimated)
- **Context Window**: 4096 tokens (supports 128K)
- **Quantization**: Q8_0 (8-bit)

---

## 🔄 Migration Guide

### For Users Running v5.02.00

1. **Backup your progress data:**
   ```bash
   copy data\progress\* backup\
   ```

2. **Uninstall old dependencies (optional):**
   ```bash
   pip uninstall ipex-llm intel-extension-for-pytorch
   ```

3. **Install llama.cpp:**
   ```bash
   winget install ggml.llamacpp
   ```

4. **Pull latest code:**
   ```bash
   git pull origin latest
   ```

5. **Restart the app:**
   ```bash
   python app.py
   ```

### Switching to Llama 3.1 (When Downloaded)

1. Download Llama 3.1 8B GGUF from HuggingFace
2. Update `models/llama31_model.py` line 31 with model path
3. In `app.py`, change:
   ```python
   from models.gptoss_model import GPTOSSModel
   # to
   from models.llama31_model import Llama31Model
   ```
4. Restart

---

## 🙏 Acknowledgments

**New Contributors:**
- **Intel GPU Team** - Arc GPU development and XPU acceleration
- **Intel AI Playground Team** - Model distribution and infrastructure
- **OpenAI** - GPT-OSS open-weight reasoning models
- **Meta** - Llama 3.1 model family
- **ggerganov & llama.cpp community** - Local inference engine

**Continued Support:**
- Microsoft (Phi 3.5 - v5.0-5.2)
- Mistral AI (Mistral 7B - v5.1-5.2)
- PyTorch team
- Hugging Face

---

## 🚀 What's Next: Version 6

Version 6 will introduce:
- Complete frontend redesign
- Real-time streaming responses
- Multi-modal support (text + images)
- Enhanced progress analytics
- Teacher dashboard
- Cloud sync for progress data
- Mobile-responsive interface

**Target Release**: Q1 2026

---

## 📝 Known Issues

1. **GPU Memory Display**: Task Manager shows "GPU Memory" instead of specific VRAM breakdown
   - **Impact**: Minor - doesn't affect functionality
   - **Workaround**: Use `nvidia-smi` equivalent for Intel Arc

2. **First Request Slow**: Initial generation after server start is slower
   - **Impact**: ~5-10s extra on first request
   - **Cause**: GPU warmup + model initialization
   - **Workaround**: None needed

3. **Reasoning Marker Not Always Present**: Some GPT-OSS responses don't include marker
   - **Impact**: Falls back to pattern-based extraction
   - **Mitigation**: Pattern fallback works well
   - **Status**: Investigating model configuration

---

## 📄 License

**Copyright © 2025 Joseph-Babu**  
All Rights Reserved - Personal Use Only

---

**Xilo AI Tutor v5.09.00**  
*Powered by Intel Arc GPU (Vulkan) & llama.cpp*
