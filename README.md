# Xilo AI Tutor - Large v5 Overhaul

**Version 5.0.10**


An advanced AI tutoring system powered by Microsoft Phi 3.5 Mini model, optimized for Intel GPU with XMX engines acceleration.

## Branches

**main**: Stable production branch
**latest**: Latest working fixes, Intel Arc B580, transformers 4.45.0, ipex-llm, frontend bugfixes

## 🚀 Features

- **Intel XPU Acceleration**: Optimized for Intel Arc GPUs with XMX engines
- **Phi 3.5 Mini Integration**: Microsoft's latest instruct-tuned language model
- **Web-based Interface**: Clean, responsive chat interface
- **Real-time GPU Monitoring**: Live Intel XPU status and memory usage
- **High Performance**: 38-49 second generation times on Intel Arc B580
- **Memory Efficient**: Smart GPU memory management with automatic cache clearing

## 🏗️ Architecture

- **Backend**: Flask server with Intel XPU PyTorch integration
- **Frontend**: HTML5/CSS3/JavaScript with responsive design
- **AI Model**: Microsoft Phi 3.5 Mini (Instruct variant)
- **Hardware**: Intel Arc GPUs with XMX engine support
- **Acceleration**: PyTorch XPU with Intel Extension

## ⚠️ SYSTEM REQUIREMENTS

### ⚡ Intel GPU Required
**This software ONLY runs on Intel GPUs with XMX engines. CPU-only execution is not supported.**

### Hardware Requirements
- **Intel Arc GPU**: Battlemage architecture (B580, A770) or newer
- **XMX Engines**: Required for AI acceleration  
- **GPU Memory**: Minimum 8GB VRAM (12GB+ recommended)
- **System RAM**: 16GB minimum
- **Storage**: 15GB free space (for model files)

### Software Requirements
- **Operating System**: Windows 10/11 (64-bit)
- **Python**: 3.8 - 3.11 (3.12+ not tested)
- **Intel GPU Drivers**: Latest version from Intel
- **PyTorch XPU**: 2.7.0+
- **Intel Extension for PyTorch**: 2.7.10+xpu

### Compatibility Notes
- **Intel Arc A-series**: Not recommended (limited XMX support)
- **Intel Integrated Graphics**: Not supported
- **NVIDIA/AMD GPUs**: Not supported
- **CPU-only execution**: Not supported

## 🛠️ Installation

### Prerequisites
```bash
# Install Intel GPU drivers first
# Download from Intel's official website

# Verify Intel GPU detection
python -c "import intel_extension_for_pytorch as ipex; print('Intel XPU available:', ipex.xpu.is_available())"
```

### Dependencies
```bash
pip install torch==2.7.0+xpu -f https://developer.intel.com/ipex-whl-stable-xpu
pip install intel-extension-for-pytorch==2.7.10+xpu -f https://developer.intel.com/ipex-whl-stable-xpu
pip install transformers
pip install flask
pip install requests
```

### Model Setup
The application will automatically download the Microsoft Phi 3.5 Mini model (~7.1GB) on first run.

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

### Configuration
- **Temperature**: 0.1-1.0 (creativity level)
- **Max Length**: 512-4096 tokens (response length)
- **Top-p**: 0.1-1.0 (nucleus sampling)

## 📊 Performance Metrics

### Intel Arc B580 Performance
- **Model Loading**: ~15-20 seconds
- **Memory Usage**: 7.12GB GPU memory
- **Generation Speed**: 38-49 seconds per response
- **Max Tokens**: 512 tokens per response
- **Concurrent Users**: Single user optimized

### Optimization Features
- Greedy decoding for consistent responses
- XPU memory cache management
- Automatic garbage collection
- Streaming response capability

## 🔧 Technical Details

### Model Configuration
```python
Generation Parameters:
- max_new_tokens: 512
- do_sample: False (greedy decoding)
- temperature: 0.7
- top_p: 0.9
- pad_token_id: tokenizer.eos_token_id
```

### Intel XPU Optimization
- Direct XPU device allocation
- Optimized attention mechanisms
- Memory-efficient inference
- Automatic precision handling

## 📁 Project Structure

```
xilov5/
├── app.py                 # Flask web server
├── models/
│   └── phi_model.py      # Phi 3.5 model wrapper
├── utils/
│   └── intel_gpu.py      # Intel XPU utilities
├── static/
│   ├── css/
│   │   └── style.css     # UI styling
│   └── js/
│       └── app.js        # Frontend JavaScript
├── templates/
│   └── index.html        # Main web interface
├── logs/                 # Application logs
└── README.md            # This file
```

## 🐛 Troubleshooting

### Common Issues

**Intel XPU not detected:**
```bash
# Verify Intel GPU drivers
dxdiag

# Check PyTorch XPU installation
python -c "import torch; print('XPU available:', torch.xpu.is_available())"
```

**Memory issues:**
- Restart the application to clear GPU memory
- Reduce max_new_tokens parameter
- Close other GPU-intensive applications

**Slow generation:**
- Ensure Intel GPU drivers are updated
- Verify XMX engines are enabled
- Check system temperature throttling

## 📈 Version History

### v5.0.10 - Latest Branch
	- ✅ Complete Intel XPU optimization
	- ✅ Phi 3.5 Mini model integration
	- ✅ Web interface redesign
	- ✅ Performance monitoring dashboard
	- ✅ Memory management improvements
	- ✅ Response formatting fixes
	- ✅ Intel Arc B580 GPU support
	- ✅ transformers 4.45.0 compatibility
	- ✅ ipex-llm 2.3.0b20251027
	- ✅ Frontend bugfixes (GPU status, chat)

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

- Microsoft for the Phi 3.5 model family
- Intel for XPU acceleration technology
- PyTorch team for XPU integration
- Transformers library by Hugging Face

---

**Xilo AI Tutor v5.00.00** - Powered by Intel XPU Technology
