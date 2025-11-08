"""
Xilo AI Tutor - Main Flask Application
Following AI Playground backend service architecture patterns
Optimized for Intel Arc GPU with IPEX-LLM
"""

# CRITICAL: Set environment variable BEFORE any imports
# This tells ipex-llm to skip its IPEX import check (PyTorch 2.6 auto-loads IPEX)
import os
os.environ['BIGDL_IMPORT_IPEX'] = 'False'

from apiflask import APIFlask
from flask import render_template, request, jsonify, Response, stream_with_context
import logging
import json
import time
from pathlib import Path

from config import Config
from models.phi_model import phi_tutor
from utils.intel_gpu import gpu_manager

# Configure logging (AI Playground pattern)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('xilo.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Initialize APIFlask (AI Playground pattern)
app = APIFlask(__name__)
app.config.from_object(Config)

# Global model status (AI Playground pattern)
model_status = {
    'status': 'initializing',  # initializing | ready | error
    'error': None,
    'device': None
}

def initialize_model():
    """Initialize Phi 3.5 model with Intel XPU optimization"""
    global model_status
    
    try:
        logger.info("=" * 60)
        logger.info("Initializing Xilo AI Tutor with Intel GPU acceleration")
        logger.info(f"Model: {Config.MODEL_NAME}")
        
        # Check Intel XPU availability
        device_info = gpu_manager.get_device_info()
        logger.info(f"Device: {device_info}")
        
        # Load model
        logger.info("Loading Phi 3.5 model...")
        phi_tutor.load_model()
        
        model_status['status'] = 'ready'
        model_status['device'] = device_info
        
        logger.info("✅ Xilo AI Tutor ready!")
        logger.info(f"Access at: http://{Config.HOST}:{Config.PORT}")
        logger.info("=" * 60)
        
    except Exception as e:
        model_status['status'] = 'error'
        model_status['error'] = str(e)
        logger.error(f"❌ Model initialization failed: {e}")
        raise

# Routes

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')

@app.route('/api/status')
def status():
    """Get system status (AI Playground pattern)"""
    try:
        return jsonify({
            "code": 0,
            "message": "success",
            "data": {
                "model_status": model_status,
                "model_info": phi_tutor.get_model_info() if model_status['status'] == 'ready' else None,
                "device": gpu_manager.get_device_info()
            }
        })
    except Exception as e:
        logger.error(f"Error getting status: {e}")
        return jsonify({"code": -1, "message": str(e)}), 500

@app.post("/api/chat")
def chat():
    """Handle chat messages (AI Playground pattern with proper error handling)"""
    try:
        data = request.get_json()
        
        # Validate request
        if not data or 'message' not in data:
            return jsonify({
                "code": -1,
                "message": "No message provided"
            }), 400
        
        user_message = data['message'].strip()
        if not user_message:
            return jsonify({
                "code": -1,
                "message": "Empty message"
            }), 400
        
        # Check model status
        if model_status['status'] != 'ready':
            return jsonify({
                "code": -1,
                "message": f"Model not ready: {model_status['status']}"
            }), 503
        
        # Get parameters
        temperature = data.get('temperature', Config.TEMPERATURE)
        max_new_tokens = data.get('max_new_tokens', 512)
        top_p = data.get('top_p', Config.TOP_P)
        
        # Validate parameters
        temperature = max(0.1, min(1.0, float(temperature)))
        max_new_tokens = max(128, min(2048, int(max_new_tokens)))
        top_p = max(0.1, min(1.0, float(top_p)))
        
        logger.info(f"Chat request: {user_message[:100]}...")
        
        # Generate response
        start_time = time.time()
        response = phi_tutor.generate_response(
            user_message,
            max_new_tokens=max_new_tokens,
            temperature=temperature,
            top_p=top_p
        )
        generation_time = time.time() - start_time
        
        logger.info(f"Response generated in {generation_time:.2f}s")
        
        return jsonify({
            "code": 0,
            "message": "success",
            "data": {
                "response": response,
                "metadata": {
                    "generation_time": round(generation_time, 2),
                    "device": model_status['device']['device'],
                    "tokens_per_second": round(len(response.split()) / generation_time, 2)
                }
            }
        })
        
    except Exception as e:
        logger.error(f"Chat error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "code": -1,
            "message": str(e)
        }), 500

@app.post("/api/chat/stream")
def chat_stream():
    """Streaming chat endpoint (AI Playground SSE pattern)"""
    try:
        data = request.get_json()
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return jsonify({"code": -1, "message": "Empty message"}), 400
        
        if model_status['status'] != 'ready':
            return jsonify({"code": -1, "message": "Model not ready"}), 503
        
        def response_generator():
            """Generator for streaming response (AI Playground pattern)"""
            try:
                # Start generation
                yield f"data: {json.dumps({'status': 'started', 'message': 'Generating response...'})}\n\n"
                
                # Generate response (if your model supports streaming)
                response = phi_tutor.generate_response(user_message)
                
                # Send chunks (simulate streaming if model doesn't support it natively)
                words = response.split()
                for i, word in enumerate(words):
                    chunk_data = {
                        'status': 'generating',
                        'chunk': word + ' ',
                        'progress': (i + 1) / len(words)
                    }
                    yield f"data: {json.dumps(chunk_data)}\n\n"
                    time.sleep(0.05)  # Smooth streaming
                
                # Send completion
                yield f"data: {json.dumps({'status': 'completed', 'full_response': response})}\n\n"
                
            except Exception as e:
                logger.error(f"Streaming error: {e}")
                yield f"data: {json.dumps({'status': 'error', 'message': str(e)})}\n\n"
        
        return Response(
            stream_with_context(response_generator()),
            content_type="text/event-stream"
        )
        
    except Exception as e:
        logger.error(f"Stream setup error: {e}")
        return jsonify({"code": -1, "message": str(e)}), 500

@app.post("/api/clear-memory")
def clear_memory():
    """Clear GPU memory (AI Playground pattern)"""
    try:
        gpu_manager.clear_memory()
        return jsonify({
            "code": 0,
            "message": "Memory cleared successfully"
        })
    except Exception as e:
        logger.error(f"Memory clear error: {e}")
        return jsonify({"code": -1, "message": str(e)}), 500

# Error handlers (AI Playground pattern)

@app.errorhandler(404)
def not_found(error):
    return jsonify({"code": -1, "message": "Endpoint not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"code": -1, "message": "Internal server error"}), 500

if __name__ == '__main__':
    import sys
    
    # Only initialize model when NOT running with reloader or when in reloader child process
    # This prevents double initialization in Flask debug mode
    is_reloader_child = os.environ.get('WERKZEUG_RUN_MAIN') == 'true'
    
    if not Config.DEBUG or is_reloader_child:
        print("""
    ██╗  ██╗██╗██╗      ██████╗     ██╗   ██╗███████╗
    ╚██╗██╔╝██║██║     ██╔═══██╗    ██║   ██║██╔════╝
     ╚███╔╝ ██║██║     ██║   ██║    ██║   ██║███████╗
     ██╔██╗ ██║██║     ██║   ██║    ██║   ██║╚════██║
    ██╔╝ ██╗██║███████╗╚██████╔╝    ╚██████╔╝███████║
    ╚═╝  ╚═╝╚═╝╚══════╝ ╚═════╝      ╚═════╝ ╚══════╝
    
    AI Tutor powered by Intel Arc GPU & Phi 3.5 (IPEX-LLM)
    Following AI Playground architecture patterns
    """)
        
        print(f"\nConfiguration:")
        print(f"  Model: {Config.MODEL_NAME}")
        print(f"  Intel XPU: Detecting after model load...")
        print(f"  Host: {Config.HOST}:{Config.PORT}")
        print()
        
        # Initialize model before starting server (AI Playground pattern)
        try:
            initialize_model()
            # Show GPU info AFTER model loads
            device_info = gpu_manager.get_device_info()
            if device_info.get('available'):
                print(f"\n✅ Intel GPU Ready: {device_info.get('name', 'Unknown')}")
                print(f"   Memory: {device_info.get('memory_allocated', 'N/A')} allocated")
        except Exception as e:
            logger.error("Failed to initialize model, but starting server anyway...")
    
    # Start Flask app
    try:
        app.run(
            host=Config.HOST,
            port=Config.PORT,
            debug=Config.DEBUG,
            threaded=True
        )
    except KeyboardInterrupt:
        print("\n\nXilo AI Tutor shutting down...")
        gpu_manager.clear_memory()
    except Exception as e:
        logger.error(f"Server startup failed: {e}")