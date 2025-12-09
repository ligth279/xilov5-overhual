"""
Chat Memory Manager for Xilo AI Tutor
Tracks conversation history for context-aware responses
Designed to be modular for future multi-user support
"""

import logging
from collections import deque
from datetime import datetime

logger = logging.getLogger(__name__)

class ChatMemory:
    """
    Manages chat history for individual users/sessions.
    Stores last N messages for context-aware conversations.
    """
    
    def __init__(self, max_history=3):
        """
        Initialize chat memory.
        
        Args:
            max_history (int): Maximum number of Q&A pairs to remember (default: 3)
        """
        self.max_history = max_history
        self.sessions = {}  # session_id -> deque of messages
        logger.info(f"ChatMemory initialized with max_history={max_history}")
    
    def add_message(self, session_id, user_message, ai_response):
        """
        Add a message pair to session history.
        
        Args:
            session_id (str): Unique session identifier
            user_message (str): User's question
            ai_response (str): AI's response
        """
        if session_id not in self.sessions:
            self.sessions[session_id] = deque(maxlen=self.max_history)
        
        message_pair = {
            'user': user_message,
            'assistant': ai_response,
            'timestamp': datetime.now().isoformat()
        }
        
        self.sessions[session_id].append(message_pair)
        logger.info(f"Added message to session {session_id}. History size: {len(self.sessions[session_id])}")
    
    def get_history(self, session_id):
        """
        Get conversation history for a session.
        
        Args:
            session_id (str): Unique session identifier
            
        Returns:
            list: List of message pairs (oldest to newest)
        """
        if session_id not in self.sessions:
            return []
        
        return list(self.sessions[session_id])
    
    def get_context_messages(self, session_id):
        """
        Get history formatted as messages for model context.
        
        Args:
            session_id (str): Unique session identifier
            
        Returns:
            list: List of message dicts for chat template
        """
        history = self.get_history(session_id)
        messages = []
        
        for pair in history:
            messages.append({"role": "user", "content": pair['user']})
            messages.append({"role": "assistant", "content": pair['assistant']})
        
        return messages
    
    def clear_session(self, session_id):
        """
        Clear history for a specific session.
        
        Args:
            session_id (str): Unique session identifier
        """
        if session_id in self.sessions:
            del self.sessions[session_id]
            logger.info(f"Cleared session {session_id}")
    
    def clear_all(self):
        """Clear all session histories."""
        self.sessions.clear()
        logger.info("Cleared all chat sessions")
    
    def get_session_count(self):
        """Get number of active sessions."""
        return len(self.sessions)
    
    def get_all_sessions(self):
        """Get list of all active session IDs."""
        return list(self.sessions.keys())

# Global memory manager instance
chat_memory = ChatMemory(max_history=3)
