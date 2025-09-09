"""
Xilo AI Tutor - Main Flask Application
Optimized for Intel GPU with XMX engines and Phi 3.5 model
"""

from flask import Flask, render_template, request, jsonify
import logging
import threading
import time
from config import Config
from models.phi_model import phi_tutor
from utils.intel_gpu import gpu_manager

# Configure logging (Windows-compatible, no emojis in console)
import sys
import codecs

# Fix Windows console encoding issues
if sys.platform.startswith('win'):
    # Set up UTF-8 encoding for file handlers, ASCII for console
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    
    file_handler = logging.FileHandler('xilo.log', encoding='utf-8')
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    
    logging.basicConfig(
        level=logging.INFO,
        handlers=[file_handler, console_handler]
    )
else:
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('xilo.log', encoding='utf-8'),
            logging.StreamHandler()
        ]
    )

logger = logging.getLogger(__name__)

# Import detailed logger
from utils.detailed_logger import xilo_logger, monitor_performance

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Global model loading status
model_loading_status = {
    'is_loading': False,
    'is_loaded': False,
    'error': None
}

@monitor_performance(xilo_logger, "model_loading")
def load_model_async():
    """Load the Phi 3.5 model asynchronously"""
    global model_loading_status
    
    try:
        model_loading_status['is_loading'] = True
        model_loading_status['error'] = None
        
        # Take initial system snapshot
        xilo_logger.log_system_snapshot("before_model_loading")
        
        logger.info("Starting Xilo AI Tutor with Intel GPU acceleration...")
        xilo_logger.log_model_state("initialization_started")
        logger.info("=" * 60)
        
        # Create cache directories
        Config.create_directories()
        
        # Load the model
        logger.info("Loading Phi 3.5 model...")
        xilo_logger.log_model_state("model_loading_started")
        phi_tutor.load_model()
        
        model_loading_status['is_loaded'] = True
        model_loading_status['is_loading'] = False
        
        # Take snapshot after successful loading
        xilo_logger.log_system_snapshot("after_model_loading")
        xilo_logger.log_model_state("model_loaded_successfully")
        
        logger.info("Xilo AI Tutor ready!")
        logger.info(f"Access the tutor at: http://{Config.HOST}:{Config.PORT}")
        logger.info("=" * 60)
        
    except Exception as e:
        model_loading_status['is_loading'] = False
        model_loading_status['error'] = str(e)
        
        # Log detailed error information
        xilo_logger.log_error(e, "model_loading_failed", {
            'suggested_rollback': 'clear_model_cache',
            'recovery_steps': [
                'Check disk space',
                'Verify internet connection', 
                'Clear model cache directory',
                'Restart application'
            ]
        })
        xilo_logger.log_model_state("model_loading_failed", {'error': str(e)})
        
        logger.error(f"Error loading model: {e}")

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')

@app.route('/logs')
def logs():
    """Logs and diagnostics page"""
    return render_template('logs.html')

@app.route('/api/status')
def status():
    """Get system and model status"""
    try:
        device_info = gpu_manager.get_device_info()
        model_info = phi_tutor.get_model_info()
        
        return jsonify({
            'status': 'success',
            'data': {
                'device': device_info,
                'model': model_info,
                'loading_status': model_loading_status
            }
        })
    except Exception as e:
        logger.error(f"Error getting status: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/info')
def info():
    """Get detailed system information"""
    try:
        device_info = gpu_manager.get_device_info()
        model_info = phi_tutor.get_model_info()
        
        return jsonify({
            'status': 'success',
            'data': {
                **model_info,
                'device': device_info,
                'config': {
                    'temperature': Config.TEMPERATURE,
                    'top_p': Config.TOP_P,
                    'max_length': Config.MAX_LENGTH
                }
            }
        })
    except Exception as e:
        logger.error(f"Error getting info: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/chat', methods=['POST'])
@monitor_performance(xilo_logger, "chat_generation")
def chat():
    """Handle chat messages"""
    try:
        data = request.get_json()
        
        if not data or 'message' not in data:
            return jsonify({
                'status': 'error',
                'message': 'No message provided'
            }), 400
        
        user_message = data['message'].strip()
        if not user_message:
            return jsonify({
                'status': 'error',
                'message': 'Empty message'
            }), 400
        
        # Check if model is loading
        if model_loading_status['is_loading']:
            return jsonify({
                'status': 'error',
                'message': 'Model is still loading. Please wait a moment and try again.'
            }), 503
        
        # Check if model failed to load
        if model_loading_status['error']:
            return jsonify({
                'status': 'error',
                'message': f'Model failed to load: {model_loading_status["error"]}'
            }), 500
        
        # Check if model is loaded
        if not model_loading_status['is_loaded']:
            return jsonify({
                'status': 'error',
                'message': 'Model not loaded yet. Please wait a moment.'
            }), 503
        
        # Get optional parameters
        temperature = data.get('temperature', Config.TEMPERATURE)
        max_length = data.get('max_length', Config.MAX_LENGTH)
        top_p = data.get('top_p', Config.TOP_P)
        
        # Validate parameters
        temperature = max(0.1, min(1.0, float(temperature)))
        max_length = max(128, min(2048, int(max_length)))
        top_p = max(0.1, min(1.0, float(top_p)))
        
        logger.info(f"User message: {user_message[:100]}...")
        logger.info(f"Settings: temp={temperature}, max_len={max_length}, top_p={top_p}")
        
        # Log chat attempt
        xilo_logger.log_model_state("chat_generation_started", {
            'message_length': len(user_message),
            'temperature': temperature,
            'max_length': max_length
        })
        
        # Generate response
        start_time = time.time()
        response = phi_tutor.generate_response(
            user_message,
            max_length=max_length,
            temperature=temperature,
            top_p=top_p
        )
        generation_time = time.time() - start_time
        
        # Log successful generation
        xilo_logger.log_model_state("chat_generation_completed", {
            'generation_time': generation_time,
            'response_length': len(response)
        })
        
        logger.info(f"Response generated in {generation_time:.2f}s")
        logger.info(f"API Response content: '{response}'")
        logger.info(f"API Response length: {len(response)} characters")
        
        return jsonify({
            'status': 'success',
            'response': response,
            'metadata': {
                'generation_time': round(generation_time, 2),
                'device': gpu_manager.get_device_info()['device'],
                'settings': {
                    'temperature': temperature,
                    'max_length': max_length,
                    'top_p': top_p
                }
            }
        })
        
    except Exception as e:
        # Log detailed error
        xilo_logger.log_error(e, "chat_generation_error", {
            'user_message_length': len(user_message) if 'user_message' in locals() else 0,
            'suggested_rollback': 'restart_model',
            'recovery_steps': [
                'Check GPU memory',
                'Clear GPU cache',
                'Restart model loading',
                'Check system resources'
            ]
        })
        
        logger.error(f"Error in chat endpoint: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Internal server error: {str(e)}'
        }), 500

@app.route('/api/clear-memory', methods=['POST'])
def clear_memory():
    """Clear GPU memory cache"""
    try:
        gpu_manager.clear_memory()
        xilo_logger.log_system_snapshot("memory_cleared")
        return jsonify({
            'status': 'success',
            'message': 'Memory cache cleared'
        })
    except Exception as e:
        xilo_logger.log_error(e, "memory_clear_failed")
        logger.error(f"Error clearing memory: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/logs/system')
def get_system_logs():
    """Get system snapshots and current state"""
    try:
        current_state = xilo_logger.get_current_system_state()
        recent_snapshots = xilo_logger.system_snapshots[-5:]  # Last 5 snapshots
        
        return jsonify({
            'status': 'success',
            'data': {
                'current_state': current_state,
                'recent_snapshots': recent_snapshots,
                'total_snapshots': len(xilo_logger.system_snapshots)
            }
        })
    except Exception as e:
        logger.error(f"Error getting system logs: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/logs/errors')
def get_error_logs():
    """Get recent error information"""
    try:
        recent_errors = xilo_logger.error_history[-10:]  # Last 10 errors
        
        return jsonify({
            'status': 'success',
            'data': {
                'recent_errors': recent_errors,
                'total_errors': len(xilo_logger.error_history)
            }
        })
    except Exception as e:
        logger.error(f"Error getting error logs: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/logs/performance')
def get_performance_logs():
    """Get performance metrics"""
    try:
        recent_performance = xilo_logger.performance_logs[-20:]  # Last 20 operations
        
        # Calculate some basic stats
        if recent_performance:
            durations = [p['duration_seconds'] for p in recent_performance]
            avg_duration = sum(durations) / len(durations)
            max_duration = max(durations)
            min_duration = min(durations)
        else:
            avg_duration = max_duration = min_duration = 0
        
        return jsonify({
            'status': 'success',
            'data': {
                'recent_operations': recent_performance,
                'stats': {
                    'total_operations': len(xilo_logger.performance_logs),
                    'average_duration': round(avg_duration, 3),
                    'max_duration': round(max_duration, 3),
                    'min_duration': round(min_duration, 3)
                }
            }
        })
    except Exception as e:
        logger.error(f"Error getting performance logs: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/logs/model')
def get_model_logs():
    """Get model state history"""
    try:
        return jsonify({
            'status': 'success',
            'data': {
                'model_states': xilo_logger.model_state_log,
                'current_status': model_loading_status
            }
        })
    except Exception as e:
        logger.error(f"Error getting model logs: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/rollback-guide')
def get_rollback_guide():
    """Generate and return rollback guide"""
    try:
        guide = xilo_logger.generate_rollback_guide()
        guide_file = xilo_logger.save_rollback_guide()
        
        return jsonify({
            'status': 'success',
            'data': {
                'guide': guide,
                'file_path': guide_file,
                'session_id': xilo_logger.session_id
            }
        })
    except Exception as e:
        logger.error(f"Error generating rollback guide: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/logs/download/<log_type>')
def download_logs(log_type):
    """Download specific log files"""
    try:
        import os
        from flask import send_file, abort
        
        if log_type not in ['system', 'errors', 'performance', 'model', 'main']:
            abort(404)
        
        if log_type == 'main':
            file_path = f"logs/xilo_main_{xilo_logger.session_id}.log"
        else:
            file_path = f"logs/{log_type}/{log_type}_{xilo_logger.session_id}.log"
        
        if os.path.exists(file_path):
            return send_file(file_path, as_attachment=True)
        else:
            abort(404)
            
    except Exception as e:
        logger.error(f"Error downloading logs: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'status': 'error',
        'message': 'Endpoint not found'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'status': 'error',
        'message': 'Internal server error'
    }), 500

if __name__ == '__main__':
    # Print startup banner (Windows-compatible)
    print("""
    ██╗  ██╗██╗██╗      ██████╗     ██╗   ██╗███████╗
    ╚██╗██╔╝██║██║     ██╔═══██╗    ██║   ██║██╔════╝
     ╚███╔╝ ██║██║     ██║   ██║    ██║   ██║███████╗
     ██╔██╗ ██║██║     ██║   ██║    ██║   ██║╚════██║
    ██╔╝ ██╗██║███████╗╚██████╔╝    ╚██████╔╝███████║
    ╚═╝  ╚═╝╚═╝╚══════╝ ╚═════╝      ╚═════╝ ╚══════╝
    
    AI Tutor powered by Intel GPU & Phi 3.5
    Optimized for XMX engines (Battlemage)
    """)
    
    print(f"Configuration:")
    print(f"   Model: {Config.MODEL_NAME}")
    print(f"   Device: {gpu_manager.device}")
    print(f"   Intel XPU: {'Available' if gpu_manager.is_available else 'Not Available'}")
    print(f"   Host: {Config.HOST}:{Config.PORT}")
    print(f"   Session ID: {xilo_logger.session_id}")
    print()
    
    # Take initial system snapshot
    xilo_logger.log_system_snapshot("application_startup")
    
    # Start model loading in background
    model_thread = threading.Thread(target=load_model_async, daemon=True)
    model_thread.start()
    
    # Start Flask app
    try:
        app.run(
            host=Config.HOST,
            port=Config.PORT,
            debug=Config.DEBUG,
            threaded=True
        )
    except KeyboardInterrupt:
        print("\nXilo AI Tutor shutting down...")
        xilo_logger.log_system_snapshot("application_shutdown")
        xilo_logger.save_rollback_guide()
    except Exception as e:
        logger.error(f"Error starting server: {e}")
        xilo_logger.log_error(e, "server_startup_failed")
        print(f"Failed to start server: {e}")
        xilo_logger.save_rollback_guide()
