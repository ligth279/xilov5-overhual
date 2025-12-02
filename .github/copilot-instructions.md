## Xilo AI Tutor Project

This project is an AI tutor website with dual-model architecture optimized for Intel GPU with XMX engines.

### Key Features:
- Intel XPU optimization with PyTorch
- Dual-model architecture (Phi 3.5 + Mistral 7B)
- Web-based interface with lesson system
- GPU-accelerated inference with 4-bit quantization

### Architecture:
- **Backend**: Flask with Intel XPU PyTorch + IPEX-LLM
- **Frontend**: HTML/CSS/JavaScript with split-view lesson interface
- **Models**: 
  - **Phi 3.5 Mini (3.8B)**: General chat and doubt clearing (STATEFUL - stores last 3 conversations)
  - **Mistral 7B**: Answer evaluation and hint generation (STATELESS - no conversation history)
- **Hardware**: Intel Arc GPU with XMX engines (Battlemage B580)

### Model Memory Management:

#### Phi 3.5 Mini (3.8B) - STATEFUL CHAT
- **Purpose**: General tutoring chat, doubt clearing (Phase 2)
- **Conversation History**: Stores last 3 user/assistant exchanges for context
- **Memory**: KV cache persists across turns within a session
- **Why**: Students need conversational context ("What did we just discuss?")
- **VRAM**: ~4-6 GB (base model + KV cache for 3 turns)

#### Mistral 7B - STATELESS HINTS
- **Purpose**: Answer evaluation, hint generation (Phase 3)
- **Conversation History**: None - each hint is independent
- **Memory**: KV cache cleared after each hint generation
- **Why**: Hints don't need conversation context - just question + answer + proximity
- **VRAM**: ~6-8 GB during generation, cache cleared immediately after
- **Memory Leak Prevention**:
  - `torch.no_grad()` wraps all generation
  - `del outputs, inputs` after use
  - `gc.collect()` + `torch.xpu.empty_cache()` after each hint
  - Phi model offloaded to CPU during Mistral generation

#### Critical Memory Differences:
1. **Phi Chat Flow**:
   ```python
   # Turn 1: "What is photosynthesis?"
   phi.generate(prompt1, history=[])  # KV cache: Turn 1
   
   # Turn 2: "Can you explain more?"
   phi.generate(prompt2, history=[turn1])  # KV cache: Turn 1 + Turn 2
   
   # Turn 3: "Give me an example"
   phi.generate(prompt3, history=[turn1, turn2])  # KV cache: Turn 1 + 2 + 3
   
   # Turn 4: "What about animals?"
   phi.generate(prompt4, history=[turn2, turn3])  # KV cache: Turn 2 + 3 + 4 (Turn 1 dropped)
   ```

2. **Mistral Hint Flow**:
   ```python
   # Hint 1: Student answers "line"
   mistral.generate("Q: stanza, A: line")  # KV cache built
   # → Hint generated
   # → torch.xpu.empty_cache()  # KV cache CLEARED
   
   # Hint 2: Student answers "verse"  
   mistral.generate("Q: stanza, A: verse")  # Fresh KV cache, no history
   # → Hint generated
   # → torch.xpu.empty_cache()  # KV cache CLEARED again
   ```

### VRAM Usage Patterns:

**Normal Operation (20GB total: 12GB dedicated + 8GB shared):**
```
Idle State:
├─ Phi 3.5 (GPU):          4-6 GB  (with 3-turn KV cache)
├─ Mistral 7B (GPU):       6-8 GB  (idle)
├─ PyTorch overhead:       2-3 GB
└─ Total:                 12-17 GB ✅

During Chat (Phi active):
├─ Phi 3.5 (GPU):          6-8 GB  (generating + KV cache)
├─ Mistral 7B (GPU):       6-8 GB  (idle)
├─ PyTorch overhead:       2-3 GB
└─ Total:                 14-19 GB ✅ (may touch shared RAM)

During Hint Generation (Mistral active):
├─ Phi 3.5 (CPU):          0 GB    (offloaded to system RAM)
├─ Mistral 7B (GPU):       8-10 GB (generating + KV cache)
├─ PyTorch overhead:       2-3 GB
└─ Total:                 10-13 GB ✅ (under 12GB dedicated!)
```

### Memory Leak Prevention (Mistral Only):

**Why Mistral needs aggressive cleanup but Phi doesn't:**
- Phi: KV cache is intentionally kept for conversation continuity
- Mistral: KV cache must be cleared to prevent accumulation across multiple student requests

**Mistral Cleanup Strategy:**
```python
# Before generation:
gc.collect()
torch.xpu.empty_cache()
self.phi_model.model.to('cpu')  # Offload Phi

# During generation:
with torch.no_grad():  # Prevent gradient accumulation
    outputs = model.generate(...)

# After generation:
del outputs, inputs  # Delete tensors
gc.collect() × 3     # Force garbage collection
torch.xpu.empty_cache()  # Clear GPU cache
self.phi_model.model.to('xpu')  # Restore Phi
```

### Setup Requirements:
- Intel GPU with XMX engines (Arc/Battlemage)
- PyTorch 2.6+ with XPU support
- ipex-llm with 4-bit quantization
- Both model files cached locally

### Project Status:
✅ Project structure created
✅ Dependencies installed successfully
✅ Intel GPU PyTorch integration working
✅ Dual-model system implemented
✅ Web interface fully functional
✅ 3-phase lesson flow (Explanation → Doubt Clearing → Assessment)
✅ Multilingual support (13 languages)
✅ AI-powered hints with spell check
✅ Progress tracking system
✅ Memory leak prevention (Mistral)
✅ Phi offloading during Mistral generation
🚀 **Xilo AI Tutor running at http://localhost:5000**

### Model Integration Details:

#### Phi 3.5 Mini (3.8B)
- **Purpose**: General tutoring chat, doubt clearing (Phase 2)
- **Strengths**: Fast responses, conversational, good for simple Q&A
- **Limitations**: Not reliable for strict answer evaluation or complex logic
- **Optimization**: ipex-llm 4-bit quantization, eager attention
- **VRAM**: ~4-6 GB
- **Conversation History**: Last 3 turns stored for context

#### Mistral 7B (NEW)
- **Purpose**: Answer evaluation, hint generation (Phase 3)
- **Strengths**: More accurate categorization, better instruction following, reliable hints
- **Format**: Uses `[INST]` tags (not chat template like Phi)
- **Optimization**: ipex-llm 4-bit quantization
- **VRAM**: ~6-8 GB during generation, cache cleared after
- **Conversation History**: None - stateless, each hint is independent
- **Why Added**: Phi 3.5 was inconsistent with answer evaluation—giving wrong hints, revealing answers, not following instructions

#### Critical Differences Between Models:
1. **Prompt Format**:
   - Phi 3.5: Chat template with roles (system/user/assistant)
   - Mistral: `<s>[INST] {prompt} [/INST]` instruction format
   
2. **Temperature**:
   - Phi 3.5: Dynamic (0.1-0.7 based on question type)
   - Mistral: Low (0.35) for consistent evaluation
   
3. **Token Limits**:
   - Phi 3.5: Dynamic (50-1024 based on question complexity)
   - Mistral: Fixed (150 for pedagogical hints)
   
4. **Use Cases**:
   - Phi 3.5: Open-ended chat, explanations, teaching (STATEFUL)
   - Mistral: Precise categorization, grading, structured output (STATELESS)

5. **Memory Management**:
   - Phi 3.5: KV cache persists for 3 turns (intentional)
   - Mistral: KV cache cleared after every hint (memory leak prevention)

### Import Order (CRITICAL for PyTorch 2.6):
```python
# 1. Import torch FIRST
import torch

# 2. Then import ipex_llm
from ipex_llm.transformers import AutoModelForCausalLM

# DO NOT import torch at module level - causes IPEX conflicts
```

### Known Issues & Solutions:
- ❌ **Issue**: Phi 3.5 gives inaccurate hints, reveals answers
  - ✅ **Solution**: Use Mistral 7B for evaluation tasks
  
- ❌ **Issue**: AI ignoring prompt instructions
  - ✅ **Solution**: Simpler prompts + lower temperature (0.35) + larger model
  
- ❌ **Issue**: Spelling hints mention wrong letters
  - ✅ **Solution**: Rule-based character comparison before AI (80% similarity check)

- ❌ **Issue**: Memory leak after multiple hint generations
  - ✅ **Solution**: Aggressive cleanup (gc.collect() × 3, torch.xpu.empty_cache(), del tensors)

- ❌ **Issue**: OUT_OF_RESOURCES error during hint generation
  - ✅ **Solution**: Offload Phi to CPU during Mistral generation

### Answer Evaluation Flow:
1. **Spelling Check** (Rule-based): 80%+ character similarity → "Check your spelling"
2. **AI Categorization** (Mistral 7B): Related vs Unrelated
3. **Related**: Explain their answer + give clue (no reveal)
4. **Unrelated**: "That's not related to the topic. Please review the material and try again." → Close quiz

### Development Notes:
- Both models load sequentially (Phi first, then Mistral)
- Answer evaluator checks Mistral first, falls back to Phi if unavailable
- Total VRAM usage: ~12-17 GB idle, 10-13 GB during hints (Phi offloaded)
- Can run on Intel Arc B580 (12GB dedicated + 8GB shared = 20GB total)
- Phi maintains conversation context (3 turns), Mistral does not
- Memory cleanup only applied to Mistral (to prevent leaks), not Phi (intentional cache)