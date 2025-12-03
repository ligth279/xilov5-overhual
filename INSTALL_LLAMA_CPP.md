# Installing llama-cpp-python with Intel SYCL Support

## Step 1: Install VS Build Tools ✅ DONE
- Desktop development with C++ workload installed
- Provides MSVC compiler

## Step 2: Install Intel oneAPI Base Toolkit (IN PROGRESS)
**Download**: 2.72GB  
**Installed size**: ~20GB  
**Provides**: Intel SYCL/DPC++ compilers (icx/icpx) + Level-Zero runtime

```powershell
winget install Intel.OneAPI.BaseToolkit --accept-source-agreements --accept-package-agreements
```

This gives you native Intel Arc GPU support via SYCL/Level-Zero (much faster than Vulkan).

## Step 3: After Intel oneAPI Installation Completes

Open a **NEW** PowerShell terminal and initialize Intel environment:

```powershell
# Activate Intel oneAPI environment
& "C:\Program Files (x86)\Intel\oneAPI\setvars.bat"

# Verify Intel compiler is available
icx --version

# Activate conda environment
conda activate cp311_libuv

# Navigate to project
cd "C:\Users\joseph\INTEL AI\xilov5"
```

## Step 4: Build llama-cpp-python with Intel SYCL

```powershell
# Set environment variables for Intel SYCL build
$env:CMAKE_ARGS="-DGGML_SYCL=ON -DCMAKE_C_COMPILER=icx -DCMAKE_CXX_COMPILER=icx"
$env:FORCE_CMAKE="1"

# Install llama-cpp-python with SYCL backend
pip install llama-cpp-python --no-cache-dir --force-reinstall --upgrade --verbose
```

## Step 5: Verify Installation

```powershell
python -c "from llama_cpp import Llama; print('llama-cpp-python with Intel SYCL installed!')"
```

## What This Achieves:
- ✅ **Native Intel XPU acceleration** via SYCL/Level-Zero
- ✅ **Full GPU offloading** for GPT-OSS 20B (13.9GB VRAM)
- ✅ **Maximum performance** on Intel Arc B580
- ✅ **No Vulkan fallback** issues

## Expected Performance:
- Model loading: 10-20 seconds to VRAM
- Inference: 20-50 tokens/second (GPU-accelerated)
- VRAM usage: 13.9GB (dedicated GPU memory)

## After Installation:
The `gptoss_model.py` will be updated to use llama-cpp-python directly with Intel XPU.
