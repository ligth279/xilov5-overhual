"""
Intel GPU Test Script for Xilo AI Tutor
Tests PyTorch XPU functionality and Intel GPU detection
"""

import sys
import torch
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_intel_gpu():
    """Test Intel GPU availability and functionality"""
    print("🔍 Testing Intel GPU Setup for Xilo AI Tutor")
    print("=" * 50)
    
    # Test basic PyTorch installation
    print(f"✅ PyTorch Version: {torch.__version__}")
    
    # Test Intel XPU availability
    try:
        import intel_extension_for_pytorch as ipex
        print(f"✅ Intel Extension for PyTorch: {ipex.__version__}")
        
        if hasattr(torch, 'xpu'):
            print("✅ PyTorch XPU support available")
            
            if torch.xpu.is_available():
                print("🚀 Intel XPU is available!")
                
                # Get device count and info
                device_count = torch.xpu.device_count()
                print(f"📊 Number of XPU devices: {device_count}")
                
                if device_count > 0:
                    current_device = torch.xpu.current_device()
                    device_name = torch.xpu.get_device_name(current_device)
                    print(f"🎯 Current device: {current_device}")
                    print(f"💻 GPU Name: {device_name}")
                    
                    # Test tensor operations
                    print("\n🧪 Testing tensor operations...")
                    device = torch.device(f"xpu:{current_device}")
                    
                    # Create test tensors
                    x = torch.randn(1000, 1000, device=device)
                    y = torch.randn(1000, 1000, device=device)
                    
                    # Perform matrix multiplication
                    result = torch.mm(x, y)
                    print(f"✅ Matrix multiplication successful: {result.shape}")
                    
                    # Test memory info
                    memory_allocated = torch.xpu.memory_allocated(current_device)
                    memory_cached = torch.xpu.memory_reserved(current_device)
                    
                    print(f"📈 Memory allocated: {memory_allocated / 1024**2:.2f} MB")
                    print(f"📈 Memory cached: {memory_cached / 1024**2:.2f} MB")
                    
                    # Clear memory
                    del x, y, result
                    torch.xpu.empty_cache()
                    print("🧹 Memory cleared")
                    
                    print("\n🎉 Intel GPU test completed successfully!")
                    print("🚀 Your Battlemage GPU with XMX engines is ready for Xilo AI Tutor!")
                    
                    return True
                    
                else:
                    print("❌ No XPU devices found")
                    return False
                    
            else:
                print("❌ Intel XPU not available")
                return False
                
        else:
            print("❌ PyTorch XPU support not available")
            return False
            
    except ImportError as e:
        print(f"❌ Intel Extension for PyTorch not available: {e}")
        return False
    except Exception as e:
        print(f"❌ Error testing Intel GPU: {e}")
        return False

def test_model_compatibility():
    """Test model loading compatibility"""
    print("\n🤖 Testing Model Compatibility")
    print("=" * 30)
    
    try:
        from transformers import AutoTokenizer, AutoModelForCausalLM
        print("✅ Transformers library available")
        
        # Test tokenizer loading (lightweight)
        print("📝 Testing tokenizer loading...")
        tokenizer = AutoTokenizer.from_pretrained("microsoft/DialoGPT-medium")
        print("✅ Tokenizer loaded successfully")
        
        print("🎯 Model compatibility test passed!")
        return True
        
    except Exception as e:
        print(f"❌ Model compatibility test failed: {e}")
        return False

if __name__ == "__main__":
    print("🎓 Xilo AI Tutor - Intel GPU Test")
    print("Optimized for Intel Battlemage with XMX engines")
    print()
    
    gpu_test = test_intel_gpu()
    model_test = test_model_compatibility()
    
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    print(f"Intel GPU Support: {'✅ PASS' if gpu_test else '❌ FAIL'}")
    print(f"Model Compatibility: {'✅ PASS' if model_test else '❌ FAIL'}")
    
    if gpu_test and model_test:
        print("\n🎉 All tests passed! Xilo AI Tutor is ready to run on your Intel GPU!")
        print("🚀 Start the application with: python app.py")
    else:
        print("\n⚠️  Some tests failed. Check the output above for details.")
        if not gpu_test:
            print("💡 GPU issues may be due to driver installation or hardware compatibility.")
        if not model_test:
            print("💡 Model issues may be due to missing dependencies.")
    
    print("\n🔧 System Information:")
    print(f"   Python: {sys.version}")
    print(f"   PyTorch: {torch.__version__}")
    try:
        import intel_extension_for_pytorch as ipex
        print(f"   Intel Extension: {ipex.__version__}")
    except ImportError:
        print("   Intel Extension: Not installed")
