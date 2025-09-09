# Xilo AI Tutor - Installation Guide

## Quick Start for Intel GPU (Battlemage)

### Prerequisites ✅

1. **Intel GPU with XMX engines** (Battlemage architecture or newer)
2. **Windows 10/11** with latest Intel GPU drivers
3. **Python 3.11+** installed on your system
4. **Git** (optional, for cloning)

### Installation Steps 🚀

#### 1. Intel GPU Driver Setup
```bash
# Make sure you have the latest Intel GPU drivers installed
# Download from: https://www.intel.com/content/www/us/en/support/articles/000005654/graphics.html
```

#### 2. Install Intel GPU PyTorch (REQUIRED)
```bash
# Install PyTorch with Intel XPU support
python -m pip install torch==2.7.0 torchvision==0.22.0 torchaudio==2.7.0 --index-url https://download.pytorch.org/whl/xpu

# Install Intel Extension for PyTorch
python -m pip install intel-extension-for-pytorch==2.7.10+xpu --extra-index-url https://pytorch-extension.intel.com/release-whl/stable/xpu/us/
```

#### 3. Install Project Dependencies
```bash
pip install -r requirements.txt
```

#### 4. Test Your Setup
```bash
python test_setup.py
```

#### 5. Start Xilo AI Tutor
```bash
python app.py
# OR use the startup script:
# Windows: start_xilo.bat
# PowerShell: .\start_xilo.ps1
```

### Usage 📖

1. **Open your browser** and go to: `http://localhost:5000`
2. **Start learning!** Ask Xilo any educational questions
3. **Monitor GPU usage** in the status indicator

### Features 🌟

- **Intel GPU Acceleration**: Fully utilizes XMX engines for fast inference
- **Phi 3.5 Model**: Latest Microsoft small language model
- **Interactive Web UI**: Clean, modern interface designed for learning
- **Adjustable Settings**: Control temperature, length, and other parameters
- **Educational Focus**: Optimized for tutoring and learning conversations
- **Real-time GPU Status**: Monitor your Intel GPU usage

### Troubleshooting 🔧

#### Intel GPU Not Detected
```bash
# Check if Intel XPU is available
python -c "import torch; print(torch.xpu.is_available())"

# Verify Intel Extension installation
python -c "import intel_extension_for_pytorch as ipex; print(ipex.__version__)"
```

#### Common Issues:

1. **GPU drivers not installed**
   - Download latest Intel Graphics drivers
   - Restart after installation

2. **PyTorch XPU not working**
   - Make sure you used the exact commands above
   - Verify Python version (3.11+ required)

3. **Model loading errors**
   - Check internet connection (model downloads ~7GB on first run)
   - Ensure sufficient storage space

4. **Performance issues**
   - Close other GPU-intensive applications
   - Try different temperature settings
   - Monitor GPU memory in system info

#### Performance Optimization:

- **Memory Settings**: Adjust `MEMORY_FRACTION` in `config.py`
- **Model Settings**: Lower `MAX_LENGTH` for faster responses
- **GPU Monitoring**: Use Intel Arc Control for detailed metrics

### Development 💻

#### Project Structure:
```
xilov5/
├── app.py                 # Main Flask application
├── config.py             # Configuration settings
├── models/
│   └── phi_model.py      # Phi 3.5 model wrapper
├── utils/
│   └── intel_gpu.py     # Intel GPU utilities
├── static/              # Web assets (CSS, JS)
├── templates/           # HTML templates
├── requirements.txt     # Python dependencies
├── test_setup.py       # Intel GPU test script
└── start_xilo.*        # Startup scripts
```

#### Key Components:

- **Intel GPU Manager**: Handles XPU device detection and optimization
- **Phi Model Wrapper**: Manages model loading and inference
- **Web Interface**: Modern, responsive UI for tutoring sessions
- **Configuration**: Centralized settings for easy customization

### System Requirements 📊

#### Minimum:
- Intel GPU with XMX support
- 8GB RAM
- 10GB storage (for model cache)
- Windows 10

#### Recommended:
- Intel Arc A-series GPU
- 16GB RAM
- SSD storage
- Windows 11

### Advanced Configuration ⚙️

#### Edit `config.py` for customization:
```python
# Model settings
MODEL_NAME = "microsoft/Phi-3.5-mini-instruct"
MAX_LENGTH = 2048
TEMPERATURE = 0.7

# GPU settings
USE_XPU = True
MEMORY_FRACTION = 0.8
```

### Support 🤝

If you encounter issues:

1. **Check system requirements** - Ensure Intel GPU compatibility
2. **Run test script** - `python test_setup.py`
3. **Check logs** - Review `xilo.log` for detailed error messages
4. **Update drivers** - Latest Intel GPU drivers often fix issues

### About Intel GPU Optimization 🎯

Xilo AI Tutor is specifically optimized for Intel GPUs:

- **XMX Engine Utilization**: Uses Intel's matrix engines for AI workloads
- **Memory Management**: Efficient GPU memory usage for large models
- **Driver Integration**: Works with Intel's latest GPU architecture
- **Performance Monitoring**: Real-time GPU status and metrics

This ensures you get the best possible performance from your Intel Battlemage GPU while running AI tutoring sessions!
