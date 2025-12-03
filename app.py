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
import argparse
from pathlib import Path

from config import Config

# Import models (lazy loaded based on CLI choice)
from utils.intel_gpu import gpu_manager
from utils.chat_memory import chat_memory
from utils.language_support import language_manager
from utils.lesson_manager import lesson_manager
from utils.answer_evaluator import answer_evaluator
from utils.progress_tracker import progress_tracker

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

# Global model instance (set by CLI choice)
active_model = None
model_choice = None

def initialize_model(model_name="gptoss"):
    """
    Initialize chosen model with Vulkan GPU optimization
    
    Args:
        model_name: "gptoss", "llama31", or "mistral"
    """
    global model_status, active_model, model_choice
    
    model_choice = model_name
    
    try:
        logger.info("=" * 60)
        logger.info(f"Xilo AI Tutor v{Config.VERSION} - Intel Arc GPU Edition")
        
        # Check Intel XPU availability
        device_info = gpu_manager.get_device_info()
        logger.info(f"Device: {device_info}")
        
        # Load chosen model
        if model_name == "gptoss":
            from models.gptoss_model import GPTOSSModel
            logger.info("Model: GPT-OSS 20B (Reasoning Model with Vulkan)")
            logger.info("Loading GPT-OSS 20B model...")
            active_model = GPTOSSModel(config={})
            model_info = active_model.load_model()
            logger.info(f"✅ GPT-OSS 20B loaded: {model_info}")
            display_name = "GPT-OSS 20B"
            
        elif model_name == "llama31":
            from models.llama31_model import Llama31Model
            logger.info("Model: Llama 3.1 8B Instruct (Direct Response with Vulkan)")
            logger.info("Loading Llama 3.1 8B model...")
            active_model = Llama31Model(config={})
            model_info = active_model.load_model()
            logger.info(f"✅ Llama 3.1 8B loaded: {model_info}")
            display_name = "Llama 3.1 8B"
            
        elif model_name == "mistral":
            from models.mistral_model import MistralModel
            logger.info("Model: Mistral 7B Instruct v0.3 (Direct Response with Vulkan)")
            logger.info("Loading Mistral 7B model...")
            active_model = MistralModel(config={})
            model_info = active_model.load_model()
            logger.info(f"✅ Mistral 7B loaded: {model_info}")
            display_name = "Mistral 7B"
            
        else:
            raise ValueError(f"Unknown model: {model_name}. Use 'gptoss', 'llama31', or 'mistral'")
        
        # Connect model to answer evaluator (unified model for both)
        answer_evaluator.phi_model = active_model  # For chat
        answer_evaluator.mistral_model = active_model  # For evaluation
        logger.info(f"✅ Answer evaluator connected to {display_name}")
        logger.info(f"   - Unified model for chat and evaluation")
        
        model_status['status'] = 'ready'
        model_status['device'] = device_info
        model_status['models'] = {
            'chat': display_name,
            'evaluation': display_name
        }
        
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

@app.route('/test')
def test_design():
    """Test page for design verification"""
    return render_template('test.html')

@app.route('/lessons')
def lessons():
    """Lessons page"""
    return render_template('lessons.html')

@app.route('/api/status')
def status():
    """Get system status (AI Playground pattern)"""
    try:
        return jsonify({
            "code": 0,
            "message": "success",
            "data": {
                "model_status": model_status,
                "model_info": active_model.get_info() if model_status['status'] == 'ready' else None,
                "device": gpu_manager.get_device_info(),
                "active_sessions": chat_memory.get_session_count(),
                "supported_languages": language_manager.get_supported_languages()
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
        
        # Get session ID (use IP address as simple session identifier for now)
        # In future, this can be replaced with proper session tokens
        session_id = data.get('session_id', request.remote_addr)
        
        # Get language preference (auto-detect or use specified)
        translation_mode = data.get('translation_mode', 'google')  # 'direct' or 'google'
        target_language = data.get('target_language', 'en')
        language_code = data.get('language', 'en')
        
        # If using Google Translate mode, always generate in English
        if translation_mode == 'google':
            language_code = 'en'
        elif not language_manager.is_supported(language_code):
            # Try to detect from message if invalid language code (for direct mode)
            detected_lang = language_manager.detect_language(user_message)
            language_code = detected_lang if detected_lang else 'en'
        
        logger.info(f"Translation mode: {translation_mode}, Target language: {target_language}, AI language: {language_code}")
        
        # Get parameters
        temperature = data.get('temperature', Config.TEMPERATURE)
        max_new_tokens = data.get('max_new_tokens', 800)  # Increased default for mathematical examples
        top_p = data.get('top_p', Config.TOP_P)
        
        # Validate parameters
        temperature = max(0.1, min(1.0, float(temperature)))
        max_new_tokens = max(128, min(2048, int(max_new_tokens)))
        top_p = max(0.1, min(1.0, float(top_p)))
        
        logger.info(f"Chat request from session {session_id}: {user_message[:100]}...")
        
        # Get conversation history (last 3 Q&A pairs)
        conversation_history = chat_memory.get_context_messages(session_id)
        
        # Generate response with conversation context and language
        start_time = time.time()
        response = active_model.generate_response(
            user_message,
            max_new_tokens=max_new_tokens,
            temperature=temperature,
            top_p=top_p,
            conversation_history=conversation_history,
            language_code=language_code
        )
        generation_time = time.time() - start_time
        
        # Save to chat memory for future context
        chat_memory.add_message(session_id, user_message, response)
        
        # Translate response if using Google Translate mode
        final_response = response
        if translation_mode == 'google' and target_language != 'en':
            try:
                from deep_translator import GoogleTranslator
                translator = GoogleTranslator(source='en', target=target_language)
                final_response = translator.translate(response)
                logger.info(f"Translated response to {target_language}")
            except Exception as e:
                logger.error(f"Translation error: {e}")
                # Fall back to original response if translation fails
                final_response = response
        
        logger.info(f"Response generated in {generation_time:.2f}s")
        
        return jsonify({
            "code": 0,
            "message": "success",
            "data": {
                "response": final_response,
                "metadata": {
                    "generation_time": round(generation_time, 2),
                    "device": model_status['device']['device'],
                    "tokens_per_second": round(len(response.split()) / generation_time, 2),
                    "conversation_length": len(conversation_history) // 2,
                    "language": language_code,
                    "translation_mode": translation_mode,
                    "target_language": target_language
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
                response = active_model.generate_response(user_message)
                
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

@app.route('/api/languages')
def get_languages():
    """Get list of supported languages"""
    try:
        return jsonify({
            "code": 0,
            "message": "success",
            "data": {
                "languages": language_manager.get_supported_languages()
            }
        })
    except Exception as e:
        logger.error(f"Error getting languages: {e}")
        return jsonify({"code": -1, "message": str(e)}), 500

@app.post("/api/clear-session")
def clear_session():
    """Clear chat history for a session"""
    try:
        data = request.get_json()
        session_id = data.get('session_id', request.remote_addr)
        chat_memory.clear_session(session_id)
        return jsonify({
            "code": 0,
            "message": "Session cleared successfully"
        })
    except Exception as e:
        logger.error(f"Session clear error: {e}")
        return jsonify({"code": -1, "message": str(e)}), 500

@app.post("/api/clear-chat")
def clear_chat():
    """Clear chat history for a session"""
    try:
        data = request.get_json()
        session_id = data.get('session_id', request.remote_addr)
        
        chat_memory.clear_session(session_id)
        
        return jsonify({
            "code": 0,
            "message": f"Chat history cleared for session {session_id}"
        })
    except Exception as e:
        logger.error(f"Chat clear error: {e}")
        return jsonify({"code": -1, "message": str(e)}), 500

@app.get("/api/chat-history")
def get_chat_history():
    """Get chat history for current session"""
    try:
        session_id = request.args.get('session_id', request.remote_addr)
        history = chat_memory.get_history(session_id)
        
        return jsonify({
            "code": 0,
            "message": "success",
            "data": {
                "session_id": session_id,
                "history": history,
                "count": len(history)
            }
        })
    except Exception as e:
        logger.error(f"History retrieval error: {e}")
        return jsonify({"code": -1, "message": str(e)}), 500

# ============================================================================
# LESSON SYSTEM API ENDPOINTS
# ============================================================================

@app.get("/api/lessons/grades")
def get_grades():
    """Get all available grades"""
    try:
        grades = lesson_manager.get_all_grades()
        return jsonify({
            "code": 0,
            "message": "success",
            "data": {"grades": grades}
        })
    except Exception as e:
        logger.error(f"Error getting grades: {e}")
        return jsonify({"code": -1, "message": str(e)}), 500

@app.get("/api/lessons/<grade>/subjects")
def get_subjects_for_grade(grade):
    """Get all subjects for a specific grade"""
    try:
        subjects = lesson_manager.get_subjects(grade)
        return jsonify({
            "code": 0,
            "message": "success",
            "data": {
                "grade": grade,
                "subjects": subjects
            }
        })
    except Exception as e:
        logger.error(f"Error getting subjects: {e}")
        return jsonify({"code": -1, "message": str(e)}), 500

@app.get("/api/lessons/<grade>/<subject>")
def get_lessons_for_subject(grade, subject):
    """Get all lessons for a specific grade and subject"""
    try:
        lessons = lesson_manager.get_lessons(grade, subject)
        return jsonify({
            "code": 0,
            "message": "success",
            "data": {
                "grade": grade,
                "subject": subject,
                "lessons": lessons
            }
        })
    except Exception as e:
        logger.error(f"Error getting lessons: {e}")
        return jsonify({"code": -1, "message": str(e)}), 500

@app.get("/api/lessons/<grade>/<subject>/<lesson_id>")
def get_lesson(grade, subject, lesson_id):
    """Get full lesson data"""
    try:
        lesson = lesson_manager.get_lesson(grade, subject, lesson_id)
        
        if not lesson:
            return jsonify({
                "code": -1,
                "message": "Lesson not found"
            }), 404
        
        return jsonify({
            "code": 0,
            "message": "success",
            "data": {"lesson": lesson}
        })
    except Exception as e:
        logger.error(f"Error getting lesson: {e}")
        return jsonify({"code": -1, "message": str(e)}), 500

@app.get("/api/lessons/<grade>/<subject>/<lesson_id>/section/<section_id>")
def get_section(grade, subject, lesson_id, section_id):
    """Get specific section from a lesson"""
    try:
        section = lesson_manager.get_section(grade, subject, lesson_id, section_id)
        
        if not section:
            return jsonify({
                "code": -1,
                "message": "Section not found"
            }), 404
        
        return jsonify({
            "code": 0,
            "message": "success",
            "data": {"section": section}
        })
    except Exception as e:
        logger.error(f"Error getting section: {e}")
        return jsonify({"code": -1, "message": str(e)}), 500

@app.post("/api/lessons/doubt-chat")
def lesson_doubt_chat():
    """
    Chat during doubt clearing phase
    Works like regular chat but scoped to a specific lesson section
    """
    try:
        data = request.get_json()
        
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
        
        if model_status['status'] != 'ready':
            return jsonify({
                "code": -1,
                "message": f"Model not ready: {model_status['status']}"
            }), 503
        
        # Get lesson context
        grade = data.get('grade')
        subject = data.get('subject')
        lesson_id = data.get('lesson_id')
        section_id = data.get('section_id')
        session_id = data.get('session_id', request.remote_addr)
        
        # Get language and translation settings
        translation_mode = data.get('translation_mode', 'google')
        target_language = data.get('target_language', 'en')
        language_code = data.get('language', 'en')
        
        # If using Google Translate mode, always generate in English
        if translation_mode == 'google':
            language_code = 'en'
        
        # Build context-aware system prompt with brevity guidelines
        context_prompt = "You are a helpful AI tutor. "
        
        # Add grade-appropriate response length guidelines
        grade_num = int(''.join(filter(str.isdigit, grade))) if grade else 5
        if grade_num <= 3:
            context_prompt += "Keep answers very short (2-3 sentences). Use simple words. "
        elif grade_num <= 6:
            context_prompt += "Keep answers brief (3-4 sentences). Be clear and direct. "
        elif grade_num <= 9:
            context_prompt += "Keep answers concise (4-5 sentences). Avoid excessive detail. "
        else:
            context_prompt += "Keep answers focused (5-6 sentences). Be thorough but concise. "
        
        if section_id:
            section = lesson_manager.get_section(grade, subject, lesson_id, section_id)
            if section:
                context_prompt += f"\n\nYou are currently teaching about: {section['title']}\n"
                context_prompt += f"Topic content: {section['content'][:500]}...\n\n"
                context_prompt += "Answer the student's questions about this topic clearly and encouragingly. "
                context_prompt += "Do NOT ramble or over-explain. Get to the point quickly."
        
        # Get conversation history for this lesson session
        lesson_session_id = f"{session_id}_lesson_{lesson_id}_{section_id}"
        conversation_history = chat_memory.get_context_messages(lesson_session_id)
        
        # Generate response
        start_time = time.time()
        response = active_model.generate_response(
            user_message,
            max_new_tokens=512,
            temperature=0.7,  # More creative for explanations
            conversation_history=conversation_history,
            system_prompt_override=context_prompt,
            language_code=language_code
        )
        generation_time = time.time() - start_time
        
        # Translate response if using Google Translate mode
        final_response = response
        if translation_mode == 'google' and target_language != 'en':
            try:
                from deep_translator import GoogleTranslator
                translator = GoogleTranslator(source='en', target=target_language)
                final_response = translator.translate(response)
                logger.info(f"Translated lesson response to {target_language}")
            except Exception as e:
                logger.error(f"Translation error: {e}")
                # Fall back to original response if translation fails
                final_response = response
        
        # Save to lesson-specific chat memory
        chat_memory.add_message(lesson_session_id, user_message, final_response)
        
        logger.info(f"Lesson doubt chat ({target_language}): {user_message[:50]}... -> Response in {generation_time:.2f}s")
        
        return jsonify({
            "code": 0,
            "message": "success",
            "data": {
                "response": final_response,
                "metadata": {
                    "generation_time": round(generation_time, 2),
                    "section_id": section_id,
                    "language": target_language
                }
            }
        })
        
    except Exception as e:
        logger.error(f"Doubt chat error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "code": -1,
            "message": str(e)
        }), 500

@app.post("/api/lessons/evaluate-answer")
def evaluate_answer():
    """Evaluate student's answer to a question"""
    try:
        data = request.get_json()
        
        # Validate request
        required_fields = ['grade', 'subject', 'lesson_id', 'section_id', 'question_id', 'answer']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    "code": -1,
                    "message": f"Missing required field: {field}"
                }), 400
        
        grade = data['grade']
        subject = data['subject']
        lesson_id = data['lesson_id']
        section_id = data['section_id']
        question_id = data['question_id']
        student_answer = data['answer'].strip()
        use_ai = data.get('use_ai', False)  # Default to simple evaluation
        
        if not student_answer:
            return jsonify({
                "code": -1,
                "message": "Empty answer"
            }), 400
        
        # Get the question data
        question_data = lesson_manager.get_question(grade, subject, lesson_id, section_id, question_id)
        
        if not question_data:
            return jsonify({
                "code": -1,
                "message": "Question not found"
            }), 404
        
        # Initialize answer evaluator with phi model if using AI evaluation
        if use_ai and not answer_evaluator.phi_model:
            answer_evaluator.phi_model = active_model
        
        # Evaluate the answer
        start_time = time.time()
        result = answer_evaluator.evaluate_answer(question_data, student_answer, use_ai=use_ai)
        evaluation_time = time.time() - start_time
        
        logger.info(f"Answer evaluated: {question_id} -> {'✓' if result['is_correct'] else '✗'} ({evaluation_time:.2f}s)")
        
        return jsonify({
            "code": 0,
            "message": "success",
            "data": {
                "evaluation": result,
                "metadata": {
                    "evaluation_time": round(evaluation_time, 2),
                    "method": "ai" if use_ai else "simple"
                }
            }
        })
        
    except Exception as e:
        logger.error(f"Answer evaluation error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "code": -1,
            "message": str(e)
        }), 500

@app.post("/api/lessons/get-hint")
def get_hint():
    """Get an intelligent hint for a question based on student's answer"""
    try:
        data = request.get_json()
        
        required_fields = ['grade', 'subject', 'lesson_id', 'section_id', 'question_id', 'hint_level']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    "code": -1,
                    "message": f"Missing required field: {field}"
                }), 400
        
        grade = data['grade']
        subject = data['subject']
        lesson_id = data['lesson_id']
        section_id = data['section_id']
        question_id = data['question_id']
        hint_level = int(data['hint_level'])
        student_answer = data.get('answer', '')  # Get student's answer if provided
        
        # Get the question data
        question_data = lesson_manager.get_question(grade, subject, lesson_id, section_id, question_id)
        
        if not question_data:
            return jsonify({
                "code": -1,
                "message": "Question not found"
            }), 404
        
        # Log the request for debugging
        logger.info(f"Hint request: level={hint_level}, has_answer={bool(student_answer)}, answer='{student_answer[:50] if student_answer else 'none'}'")
        
        # Get hint (AI-powered if student_answer provided)
        hint = answer_evaluator.get_hint(question_data, hint_level, student_answer)
        
        logger.info(f"Generated hint: {hint[:100]}...")
        
        # Check if answer is completely unrelated (AI returns CLOSE_QUIZ)
        if hint == "CLOSE_QUIZ":
            return jsonify({
                "code": 0,
                "message": "answer_unrelated",
                "data": {
                    "hint": "That answer doesn't relate to this topic. Let's review the material and try again.",
                    "hint_level": hint_level,
                    "close_quiz": True  # Signal frontend to close quiz and restart section
                }
            })
        
        # Check if hint suggests student should retry section (review needed)
        hint_lower = hint.lower()
        should_retry_section = (
            "review the material" in hint_lower or 
            "not related to the topic" in hint_lower
        )
        
        return jsonify({
            "code": 0,
            "message": "success",
            "data": {
                "hint": hint,
                "hint_level": hint_level,
                "should_retry_section": should_retry_section
            }
        })
        
    except Exception as e:
        logger.error(f"Get hint error: {e}")
        return jsonify({
            "code": -1, "message": str(e)}), 500

@app.get("/api/lessons/search")
def search_lessons():
    """Search for lessons by keyword"""
    try:
        query = request.args.get('q', '').strip()
        
        if not query:
            return jsonify({
                "code": -1,
                "message": "No search query provided"
            }), 400
        
        results = lesson_manager.search_lessons(query)
        
        return jsonify({
            "code": 0,
            "message": "success",
            "data": {
                "query": query,
                "results": results,
                "count": len(results)
            }
        })
        
    except Exception as e:
        logger.error(f"Search error: {e}")
        return jsonify({"code": -1, "message": str(e)}), 500

@app.post("/api/lessons/clear-session")
def clear_lesson_session():
    """Clear chat history for a lesson session"""
    try:
        data = request.get_json()
        session_id = data.get('session_id', request.remote_addr)
        lesson_id = data.get('lesson_id')
        section_id = data.get('section_id')
        
        lesson_session_id = f"{session_id}_lesson_{lesson_id}_{section_id}"
        chat_memory.clear_session(lesson_session_id)
        
        return jsonify({
            "code": 0,
            "message": "Lesson session cleared successfully"
        })
    except Exception as e:
        logger.error(f"Lesson session clear error: {e}")
        return jsonify({"code": -1, "message": str(e)}), 500

# ============================================================================
# PROGRESS TRACKING API
# ============================================================================

@app.post("/api/progress/start-lesson")
def start_lesson_progress():
    """Start or resume a lesson"""
    try:
        data = request.get_json()
        user_id = data.get('user_id', request.remote_addr)
        grade = data.get('grade')
        subject = data.get('subject')
        lesson_id = data.get('lesson_id')
        
        if not all([grade, subject, lesson_id]):
            return jsonify({
                "code": -1,
                "message": "Missing required fields: grade, subject, lesson_id"
            }), 400
        
        lesson_progress = progress_tracker.start_lesson(user_id, grade, subject, lesson_id)
        
        return jsonify({
            "code": 0,
            "message": "success",
            "data": {"progress": lesson_progress}
        })
    except Exception as e:
        logger.error(f"Start lesson error: {e}")
        return jsonify({"code": -1, "message": str(e)}), 500

@app.post("/api/progress/update-section")
def update_section_progress():
    """Update progress for a section"""
    try:
        data = request.get_json()
        user_id = data.get('user_id', request.remote_addr)
        grade = data.get('grade')
        subject = data.get('subject')
        lesson_id = data.get('lesson_id')
        section_id = data.get('section_id')
        status = data.get('status', 'in_progress')  # in_progress | completed
        
        if not all([grade, subject, lesson_id, section_id]):
            return jsonify({
                "code": -1,
                "message": "Missing required fields"
            }), 400
        
        lesson_progress = progress_tracker.update_section_progress(
            user_id, grade, subject, lesson_id, section_id, status
        )
        
        return jsonify({
            "code": 0,
            "message": "success",
            "data": {"progress": lesson_progress}
        })
    except Exception as e:
        logger.error(f"Update section error: {e}")
        return jsonify({"code": -1, "message": str(e)}), 500

@app.post("/api/progress/record-answer")
def record_answer_progress():
    """Record a question answer"""
    try:
        data = request.get_json()
        user_id = data.get('user_id', request.remote_addr)
        grade = data.get('grade')
        subject = data.get('subject')
        lesson_id = data.get('lesson_id')
        question_id = data.get('question_id')
        is_correct = data.get('is_correct', False)
        hints_used = data.get('hints_used', 0)
        
        if not all([grade, subject, lesson_id, question_id]):
            return jsonify({
                "code": -1,
                "message": "Missing required fields"
            }), 400
        
        question_progress = progress_tracker.record_answer(
            user_id, grade, subject, lesson_id, question_id, is_correct, hints_used
        )
        
        return jsonify({
            "code": 0,
            "message": "success",
            "data": {"question_progress": question_progress}
        })
    except Exception as e:
        logger.error(f"Record answer error: {e}")
        return jsonify({"code": -1, "message": str(e)}), 500

@app.post("/api/progress/complete-lesson")
def complete_lesson_progress():
    """Mark a lesson as completed"""
    try:
        data = request.get_json()
        user_id = data.get('user_id', request.remote_addr)
        grade = data.get('grade')
        subject = data.get('subject')
        lesson_id = data.get('lesson_id')
        
        if not all([grade, subject, lesson_id]):
            return jsonify({
                "code": -1,
                "message": "Missing required fields"
            }), 400
        
        lesson_progress = progress_tracker.complete_lesson(user_id, grade, subject, lesson_id)
        
        if not lesson_progress:
            return jsonify({
                "code": -1,
                "message": "Lesson not found or not started"
            }), 404
        
        return jsonify({
            "code": 0,
            "message": "success",
            "data": {"progress": lesson_progress}
        })
    except Exception as e:
        logger.error(f"Complete lesson error: {e}")
        return jsonify({"code": -1, "message": str(e)}), 500

@app.get("/api/progress/lesson")
def get_lesson_progress():
    """Get progress for a specific lesson"""
    try:
        user_id = request.args.get('user_id', request.remote_addr)
        grade = request.args.get('grade')
        subject = request.args.get('subject')
        lesson_id = request.args.get('lesson_id')
        
        if not all([grade, subject, lesson_id]):
            return jsonify({
                "code": -1,
                "message": "Missing required parameters"
            }), 400
        
        lesson_progress = progress_tracker.get_lesson_progress(user_id, grade, subject, lesson_id)
        
        return jsonify({
            "code": 0,
            "message": "success",
            "data": {"progress": lesson_progress}
        })
    except Exception as e:
        logger.error(f"Get lesson progress error: {e}")
        return jsonify({"code": -1, "message": str(e)}), 500

@app.get("/api/progress/user")
def get_user_progress():
    """Get complete user progress"""
    try:
        user_id = request.args.get('user_id', request.remote_addr)
        progress = progress_tracker.get_user_progress(user_id)
        
        return jsonify({
            "code": 0,
            "message": "success",
            "data": {"progress": progress}
        })
    except Exception as e:
        logger.error(f"Get user progress error: {e}")
        return jsonify({"code": -1, "message": str(e)}), 500

@app.get("/api/progress/dashboard")
def get_dashboard_stats():
    """Get user stats for dashboard"""
    try:
        user_id = request.args.get('user_id', request.remote_addr)
        stats = progress_tracker.get_dashboard_stats(user_id)
        
        return jsonify({
            "code": 0,
            "message": "success",
            "data": {"stats": stats}
        })
    except Exception as e:
        logger.error(f"Get dashboard stats error: {e}")
        return jsonify({"code": -1, "message": str(e)}), 500

@app.get("/api/progress/subject")
def get_subject_progress():
    """Get progress for all lessons in a subject"""
    try:
        user_id = request.args.get('user_id', request.remote_addr)
        grade = request.args.get('grade')
        subject = request.args.get('subject')
        
        if not all([grade, subject]):
            return jsonify({
                "code": -1,
                "message": "Missing required parameters: grade, subject"
            }), 400
        
        subject_progress = progress_tracker.get_subject_progress(user_id, grade, subject)
        
        return jsonify({
            "code": 0,
            "message": "success",
            "data": {"progress": subject_progress}
        })
    except Exception as e:
        logger.error(f"Get subject progress error: {e}")
        return jsonify({"code": -1, "message": str(e)}), 500

@app.post("/api/progress/add-time")
def add_study_time():
    """Add study time for a lesson"""
    try:
        data = request.get_json()
        user_id = data.get('user_id', request.remote_addr)
        grade = data.get('grade')
        subject = data.get('subject')
        lesson_id = data.get('lesson_id')
        minutes = data.get('minutes', 0)
        
        if not all([grade, subject, lesson_id]):
            return jsonify({
                "code": -1,
                "message": "Missing required fields"
            }), 400
        
        progress_tracker.add_study_time(user_id, grade, subject, lesson_id, minutes)
        
        return jsonify({
            "code": 0,
            "message": "Study time recorded"
        })
    except Exception as e:
        logger.error(f"Add study time error: {e}")
        return jsonify({"code": -1, "message": str(e)}), 500

@app.post("/api/progress/reset-lesson")
def reset_lesson_progress():
    """Reset progress for a lesson"""
    try:
        data = request.get_json()
        user_id = data.get('user_id', request.remote_addr)
        grade = data.get('grade')
        subject = data.get('subject')
        lesson_id = data.get('lesson_id')
        
        if not all([grade, subject, lesson_id]):
            return jsonify({
                "code": -1,
                "message": "Missing required fields"
            }), 400
        
        success = progress_tracker.reset_lesson(user_id, grade, subject, lesson_id)
        
        return jsonify({
            "code": 0 if success else -1,
            "message": "Lesson reset successfully" if success else "Lesson not found"
        })
    except Exception as e:
        logger.error(f"Reset lesson error: {e}")
        return jsonify({"code": -1, "message": str(e)}), 500

@app.get("/api/progress/check-prerequisites")
def check_prerequisites():
    """Check if user has completed prerequisite lessons"""
    try:
        user_id = request.args.get('user_id', request.remote_addr)
        prerequisites = request.args.get('prerequisites', '').split(',')
        prerequisites = [p.strip() for p in prerequisites if p.strip()]
        
        can_access = progress_tracker.check_prerequisites(user_id, prerequisites)
        
        return jsonify({
            "code": 0,
            "message": "success",
            "data": {
                "can_access": can_access,
                "prerequisites": prerequisites
            }
        })
    except Exception as e:
        logger.error(f"Check prerequisites error: {e}")
        return jsonify({"code": -1, "message": str(e)}), 500

# ============================================================================
# END PROGRESS TRACKING API
# ============================================================================

# ============================================================================
# END LESSON SYSTEM API
# ============================================================================

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
        
        # Parse CLI arguments for model selection
        parser = argparse.ArgumentParser(description='Xilo AI Tutor - Intel Arc B580 Optimized')
        parser.add_argument('--model', choices=['gptoss', 'llama31', 'mistral'], default='gptoss',
                          help='Choose AI model: gptoss (GPT-OSS 20B reasoning) or llama31 (Llama 3.1 8B direct) or mistral (Mistral 7B direct)')
        args = parser.parse_args()
        
        # Initialize model before starting server (AI Playground pattern)
        try:
            print(f"Loading model: {args.model.upper()}")
            initialize_model(args.model)
            # Show GPU info AFTER model loads
            device_info = gpu_manager.get_device_info()
            if device_info.get('available'):
                print(f"\n✅ Intel GPU Ready: {device_info.get('name', 'Unknown')}")
                print(f"   Memory: {device_info.get('memory_allocated', 'N/A')} allocated")
                print(f"   Model: {model_choice}")
        except Exception as e:
            logger.error("Failed to initialize model, but starting server anyway...")
    
    # Start Flask app
    try:
        app.run(
            host=Config.HOST,
            port=Config.PORT,
            debug=Config.DEBUG,
            use_reloader=False,  # Disable auto-reload to prevent restarts during model operations
            threaded=True
        )
    except KeyboardInterrupt:
        print("\n\nXilo AI Tutor shutting down...")
        gpu_manager.clear_memory()
    except Exception as e:
        logger.error(f"Server startup failed: {e}")