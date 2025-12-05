// Chat functionality
class ChatApp {
  constructor() {
    this.messages = document.getElementById('chatMessages');
    this.input = document.getElementById('chatInput');
    this.sendBtn = document.getElementById('sendBtn');
    this.status = document.getElementById('statusText');
    this.languageSelect = document.getElementById('languageSelect');
    this.translationMode = document.getElementById('translationMode');
    this.currentLanguage = 'en'; // Track current language
    
    this.init();
  }
  
  init() {
    // Send button
    this.sendBtn.addEventListener('click', () => this.send());
    
    // Enter to send (Shift+Enter for new line)
    this.input.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        this.send();
      }
    });
    
    // Auto-resize textarea
    this.input.addEventListener('input', () => {
      this.input.style.height = 'auto';
      this.input.style.height = this.input.scrollHeight + 'px';
    });
    
    // Language change feedback (only if element exists)
    if (this.languageSelect) {
      this.languageSelect.addEventListener('change', () => {
        const newLang = this.languageSelect.value;
        const langName = this.languageSelect.options[this.languageSelect.selectedIndex].text;
        
        // If language changed, clear conversation history
        if (newLang !== this.currentLanguage) {
          this.clearConversationHistory();
          this.currentLanguage = newLang;
          this.setStatus(`Language changed to ${langName} - Conversation reset`);
        } else {
          this.setStatus(`Language: ${langName}`);
        }
        
        setTimeout(() => this.setStatus('Ready'), 2000);
      });
    }
    
    // Translation mode toggle feedback (only if element exists)
    if (this.translationMode) {
      this.translationMode.addEventListener('change', () => {
        const mode = this.translationMode.checked ? 'AI Translation (Beta)' : 'Deep Translation';
        this.setStatus(`Using: ${mode}`);
        setTimeout(() => this.setStatus('Ready'), 2000);
      });
    }
  }
  
  async send() {
    const text = this.input.value.trim();
    if (!text) return;
    
    // Clear input
    this.input.value = '';
    this.input.style.height = 'auto';
    
    // Add user message
    this.addMessage(text, 'user');
    
    // Show typing indicator
    this.setStatus('AI is thinking...');
    this.sendBtn.disabled = true;
    
    const typingId = this.addTyping();
    
    try {
      // Call API with language settings
      const body = { message: text };
      
      // Add language settings if available
      if (this.languageSelect) {
        body.language = this.languageSelect.value;
        body.target_language = this.languageSelect.value;
      }
      if (this.translationMode) {
        // unchecked = deep (google), checked = ai (direct)
        body.translation_mode = this.translationMode.checked ? 'direct' : 'google';
      }
      
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body)
      });
      
      const data = await response.json();
      
      // Remove typing indicator
      this.removeTyping(typingId);
      
      if (data.code === 0) {
        this.addMessage(data.data.response, 'assistant');
        this.setStatus('Ready');
      } else {
        this.addMessage('Sorry, I encountered an error: ' + data.message, 'assistant');
        this.setStatus('Error');
      }
    } catch (error) {
      console.error('Chat error:', error);
      this.removeTyping(typingId);
      this.addMessage('Sorry, I couldn\'t connect to the server.', 'assistant');
      this.setStatus('Connection error');
    } finally {
      this.sendBtn.disabled = false;
      this.input.focus();
    }
  }
  
  addMessage(text, role) {
    const msg = document.createElement('div');
    msg.className = `message ${role}`;
    
    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    avatar.textContent = role === 'user' ? 'Y' : 'AI';
    
    const content = document.createElement('div');
    content.className = 'message-content';
    
    const p = document.createElement('p');
    p.textContent = text;
    
    content.appendChild(p);
    msg.appendChild(avatar);
    msg.appendChild(content);
    
    this.messages.appendChild(msg);
    this.scrollToBottom();
  }
  
  addTyping() {
    const typing = document.createElement('div');
    typing.className = 'message assistant';
    typing.id = 'typing-' + Date.now();
    
    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    avatar.textContent = 'AI';
    
    const indicator = document.createElement('div');
    indicator.className = 'typing-indicator';
    indicator.innerHTML = '<span></span><span></span><span></span>';
    
    typing.appendChild(avatar);
    typing.appendChild(indicator);
    this.messages.appendChild(typing);
    this.scrollToBottom();
    
    return typing.id;
  }
  
  removeTyping(id) {
    const typing = document.getElementById(id);
    if (typing) typing.remove();
  }
  
  setStatus(text) {
    this.status.textContent = text;
  }
  
  scrollToBottom() {
    this.messages.scrollTop = this.messages.scrollHeight;
  }
  
  clearConversationHistory() {
    // Call backend to clear session memory
    fetch('/api/chat/clear-history', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' }
    }).catch(err => console.error('Failed to clear history:', err));
  }

  // Mobile keyboard handling
  initMobileKeyboardFix() {
    const input = this.input;
    
    // Scroll input into view when keyboard appears
    input.addEventListener('focus', () => {
      setTimeout(() => {
        input.scrollIntoView({ behavior: 'smooth', block: 'end' });
      }, 300); // Wait for keyboard animation
    });

    // iOS viewport fix
    if (/iPhone|iPad|iPod/.test(navigator.userAgent)) {
      const viewportMeta = document.querySelector('meta[name="viewport"]');
      const originalContent = viewportMeta.content;

      input.addEventListener('focus', () => {
        viewportMeta.content = 'width=device-width, initial-scale=1, maximum-scale=1';
      });

      input.addEventListener('blur', () => {
        viewportMeta.content = originalContent;
      });
    }
  }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
  const app = new ChatApp();
  app.initMobileKeyboardFix();
});
