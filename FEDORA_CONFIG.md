# Fedora 41 Configuration - Full GPU Performance

When you migrate to Fedora 41, restore these settings for full GPU acceleration without crashes.

## Llama 3.1 Model (llama31_model.py)

Replace the `cmd` array in `load_model()` method (around line 70-77):

```python
cmd = [
    self.llama_server,
    "-m", self.model_path,
    "-c", "4096",        # Full context size
    "-ngl", "-1",        # ALL GPU layers (Fedora handles this properly)
    "--port", "8081",
    "--host", "localhost"
]
```

## GPT-OSS Model (gptoss_model.py)

```python
cmd = [
    self.llama_server,
    "-m", self.model_path,
    "-c", "2048",
    "-ngl", "-1",        # ALL GPU layers
    "--port", "8081",
    "--host", "localhost"
]
```

## Mistral Model (mistral_model.py)

```python
cmd = [
    self.llama_server,
    "-m", self.model_path,
    "--host", "127.0.0.1",
    "--port", "8081",
    "-ngl", "99",        # All layers
    "-c", "8192",
    "-t", "8"
]
```

## Expected Performance on Fedora 41
- Llama 3.1 8B: 8-12 tok/s (vs 3-4 on Windows)
- GPT-OSS 20B: 5-8 tok/s (vs 2-3 on Windows)
- Mistral 7B: 10-15 tok/s (vs 4-6 on Windows)
- No crashes, stable compute queue usage

## Why Fedora is Better
- Intel Arc drivers use proper compute queues
- SYCL backend available (even faster than Vulkan)
- Kernel-level optimizations for Intel GPUs
- Open-source drivers updated frequently
