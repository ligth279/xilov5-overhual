// Xilo AI Tutor - Frontend JavaScript
class XiloChat {
    constructor() {
        this.chatMessages = document.getElementById('chat-messages');
        this.userInput = document.getElementById('user-input');
        this.sendButton = document.getElementById('send-button');
        this.loadingMessage = document.getElementById('loading-message');
        this.gpuStatus = document.getElementById('gpu-status');
        this.charCount = document.getElementById('char-count');
        this.tempValue = document.getElementById('temp-value');
        this.lengthValue = document.getElementById('length-value');
        
        this.isLoading = false;
        this.messageHistory = [];
        
        this.init();
    }
    
    init() {
        // Event listeners
        this.sendButton.addEventListener('click', () => this.sendMessage());
        this.userInput.addEventListener('keydown', (e) => this.handleKeyPress(e));
        this.userInput.addEventListener('input', () => this.updateCharCount());
        
        // Settings listeners
        document.getElementById('temperature').addEventListener('input', (e) => {
            this.tempValue.textContent = e.target.value;
        });
        
        document.getElementById('max-length').addEventListener('input', (e) => {
            this.lengthValue.textContent = e.target.value;
        });
        
        // Auto-resize textarea
        this.userInput.addEventListener('input', () => this.autoResize());
        
        // Load system info and status
        this.loadSystemInfo();
        this.updateGPUStatus();
        
        // Focus input
        this.userInput.focus();
        
        console.log('🚀 Xilo AI Tutor initialized!');
    }
    
    handleKeyPress(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            this.sendMessage();
        }
    }
    
    autoResize() {
        this.userInput.style.height = 'auto';
        this.userInput.style.height = Math.min(this.userInput.scrollHeight, 120) + 'px';
    }
    
    updateCharCount() {
        const count = this.userInput.value.length;
        this.charCount.textContent = count;
        
        if (count > 800) {
            this.charCount.style.color = '#ef4444';
        } else if (count > 600) {
            this.charCount.style.color = '#f59e0b';
        } else {
            this.charCount.style.color = '#64748b';
        }
    }
    
    async loadSystemInfo() {
        try {
            const response = await fetch('/api/info');
            const data = await response.json();
            
            if (data.status === 'success') {
                this.systemInfo = data.data;
                console.log('System info loaded:', this.systemInfo);
            }
        } catch (error) {
            console.error('Error loading system info:', error);
        }
    }
    
    async updateGPUStatus() {
        try {
            const response = await fetch('/api/status');
            const data = await response.json();
            
            const statusElement = this.gpuStatus;
            
            if (data.status === 'success') {
                const deviceInfo = data.data.device;
                
                if (deviceInfo.available && deviceInfo.type === 'Intel XPU') {
                    statusElement.className = 'gpu-status';
                    statusElement.innerHTML = `
                        <i class="fas fa-microchip"></i>
                        <span>Intel GPU Ready</span>
                    `;
                } else {
                    statusElement.className = 'gpu-status error';
                    statusElement.innerHTML = `
                        <i class="fas fa-exclamation-triangle"></i>
                        <span>CPU Mode</span>
                    `;
                }
            } else {
                statusElement.className = 'gpu-status loading';
                statusElement.innerHTML = `
                    <i class="fas fa-spinner fa-spin"></i>
                    <span>Loading...</span>
                `;
            }
        } catch (error) {
            console.error('Error updating GPU status:', error);
            this.gpuStatus.className = 'gpu-status error';
            this.gpuStatus.innerHTML = `
                <i class="fas fa-exclamation-triangle"></i>
                <span>Status Unknown</span>
            `;
        }
    }
    
    async sendMessage(message = null) {
        const text = message || this.userInput.value.trim();
        
        if (!text || this.isLoading) return;
        
        // Clear input if not from suggestion
        if (!message) {
            this.userInput.value = '';
            this.updateCharCount();
            this.autoResize();
        }
        
        // Add user message
        this.addMessage(text, 'user');
        
        // Show loading
        this.showLoading();
        
        try {
            // Get settings
            const temperature = parseFloat(document.getElementById('temperature').value);
            const maxLength = parseInt(document.getElementById('max-length').value);
            
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    message: text,
                    temperature: temperature,
                    max_length: maxLength
                })
            });
            
            const data = await response.json();
            console.log('API Response:', data); // DEBUG
            
            if (data.status === 'success') {
                console.log('Adding bot message:', data.response); // DEBUG
                this.addMessage(data.response, 'bot');
                this.messageHistory.push({ user: text, bot: data.response });
            } else {
                this.addMessage(`Sorry, I encountered an error: ${data.message}`, 'bot', true);
            }
            
        } catch (error) {
            console.error('Error sending message:', error);
            this.addMessage('Sorry, I\'m having trouble connecting. Please try again.', 'bot', true);
        } finally {
            this.hideLoading();
        }
    }
    
    addMessage(text, type, isError = false) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type}-message`;
        
        const isUser = type === 'user';
        const iconClass = isUser ? 'fas fa-user' : (isError ? 'fas fa-exclamation-triangle' : 'fas fa-robot');
        
        // Format bot messages with markdown-like formatting
        const formattedText = isUser ? text : this.formatBotMessage(text);
        
        messageDiv.innerHTML = `
            <div class="message-content">
                <div class="message-avatar">
                    <i class="${iconClass}"></i>
                </div>
                <div class="message-text">
                    ${formattedText}
                </div>
            </div>
        `;
        
        // Insert before loading message if it exists and is properly attached
        if (this.loadingMessage.style.display !== 'none' && 
            this.loadingMessage.parentNode === this.chatMessages) {
            this.chatMessages.insertBefore(messageDiv, this.loadingMessage);
        } else {
            this.chatMessages.appendChild(messageDiv);
        }
        
        // Scroll to bottom with smooth animation
        setTimeout(() => {
            messageDiv.scrollIntoView({ behavior: 'smooth', block: 'end' });
        }, 100);
        
        // Add entrance animation
        setTimeout(() => {
            messageDiv.style.opacity = '0';
            messageDiv.style.transform = 'translateY(20px)';
            messageDiv.style.transition = 'all 0.3s ease';
            
            setTimeout(() => {
                messageDiv.style.opacity = '1';
                messageDiv.style.transform = 'translateY(0)';
            }, 10);
        }, 0);
    }
    
    formatBotMessage(text) {
        // Format plain text responses with proper line breaks and paragraphs
        return text
            .replace(/\n\n+/g, '</p><p>')  // Double line breaks = new paragraphs
            .replace(/\n/g, '<br>')        // Single line breaks = <br>
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')  // **bold**
            .replace(/\*(.*?)\*/g, '<em>$1</em>')              // *italic*
            .replace(/`(.*?)`/g, '<code>$1</code>')            // `code`
            .replace(/^(.+)$/m, '<p>$1</p>');                  // Wrap in paragraphs
    }
    
    showLoading() {
        this.isLoading = true;
        this.sendButton.disabled = true;
        this.loadingMessage.style.display = 'block';
        
        // Scroll to loading message
        setTimeout(() => {
            this.loadingMessage.scrollIntoView({ behavior: 'smooth', block: 'end' });
        }, 100);
    }
    
    hideLoading() {
        this.isLoading = false;
        this.sendButton.disabled = false;
        this.loadingMessage.style.display = 'none';
        this.userInput.focus();
    }
    
    exportChat() {
        const chatData = {
            timestamp: new Date().toISOString(),
            messages: this.messageHistory,
            systemInfo: this.systemInfo
        };
        
        const blob = new Blob([JSON.stringify(chatData, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        
        const a = document.createElement('a');
        a.href = url;
        a.download = `xilo-chat-${new Date().toISOString().split('T')[0]}.json`;
        a.click();
        
        URL.revokeObjectURL(url);
    }
}

// Settings functions
function toggleSettings() {
    const panel = document.getElementById('settings-panel');
    panel.classList.toggle('open');
}

function showInfo() {
    const modal = document.getElementById('info-modal');
    const modalBody = document.getElementById('modal-body');
    
    modal.classList.add('show');
    modalBody.innerHTML = '<div style="text-align: center; padding: 2rem;"><i class="fas fa-spinner fa-spin"></i> Loading...</div>';
    
    // Load system info
    fetch('/api/info')
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                modalBody.innerHTML = `
                    <div style="margin-bottom: 1.5rem;">
                        <h4 style="color: var(--text-primary); margin-bottom: 0.5rem;">🤖 Model Information</h4>
                        <p><strong>Model:</strong> ${data.data.model}</p>
                        <p><strong>Status:</strong> <span style="color: var(--success-color);">${data.data.status}</span></p>
                        <p><strong>Max Length:</strong> ${data.data.max_length} tokens</p>
                    </div>
                    
                    <div style="margin-bottom: 1.5rem;">
                        <h4 style="color: var(--text-primary); margin-bottom: 0.5rem;">🔧 Device Information</h4>
                        <p><strong>Device:</strong> ${data.data.device.device}</p>
                        <p><strong>Type:</strong> ${data.data.device.type}</p>
                        <p><strong>Available:</strong> ${data.data.device.available ? 'Yes' : 'No'}</p>
                        ${data.data.device.name ? `<p><strong>GPU:</strong> ${data.data.device.name}</p>` : ''}
                        ${data.data.device.memory_allocated ? `<p><strong>Memory Allocated:</strong> ${data.data.device.memory_allocated}</p>` : ''}
                    </div>
                    
                    <div style="margin-bottom: 1.5rem;">
                        <h4 style="color: var(--text-primary); margin-bottom: 0.5rem;">📊 Performance</h4>
                        <p><strong>Intel XPU Acceleration:</strong> ${data.data.device.available && data.data.device.type === 'Intel XPU' ? '✅ Enabled' : '❌ Disabled'}</p>
                        <p><strong>XMX Engine Support:</strong> ${data.data.device.available ? '✅ Active' : '❌ Inactive'}</p>
                    </div>
                    
                    <div style="text-align: center; margin-top: 2rem;">
                        <button onclick="xiloChat.exportChat()" style="background: var(--gradient-primary); border: none; color: white; padding: 0.75rem 1.5rem; border-radius: 0.5rem; cursor: pointer;">
                            <i class="fas fa-download"></i> Export Chat History
                        </button>
                    </div>
                `;
            } else {
                modalBody.innerHTML = `
                    <div style="text-align: center; color: var(--danger-color);">
                        <i class="fas fa-exclamation-triangle" style="font-size: 2rem; margin-bottom: 1rem;"></i>
                        <p>Error loading system information</p>
                        <p style="font-size: 0.875rem; color: var(--text-muted);">${data.message}</p>
                    </div>
                `;
            }
        })
        .catch(error => {
            console.error('Error loading system info:', error);
            modalBody.innerHTML = `
                <div style="text-align: center; color: var(--danger-color);">
                    <i class="fas fa-exclamation-triangle" style="font-size: 2rem; margin-bottom: 1rem;"></i>
                    <p>Connection error</p>
                </div>
            `;
        });
}

function closeModal() {
    document.getElementById('info-modal').classList.remove('show');
}

function sendSuggestion(message) {
    xiloChat.sendMessage(message);
}

// Close modal on background click
document.getElementById('info-modal').addEventListener('click', (e) => {
    if (e.target.id === 'info-modal') {
        closeModal();
    }
});

// Close settings when clicking outside
document.addEventListener('click', (e) => {
    const settingsPanel = document.getElementById('settings-panel');
    if (!settingsPanel.contains(e.target) && settingsPanel.classList.contains('open')) {
        settingsPanel.classList.remove('open');
    }
});

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.xiloChat = new XiloChat();
});

// Prevent form submission on Enter in input
document.addEventListener('keydown', (e) => {
    if (e.target.id === 'user-input' && e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
    }
});

// Add some helpful console messages
console.log(`
🚀 Xilo AI Tutor - Intel GPU Powered Learning
Built with ❤️ for Intel GPUs with XMX engines
`);

// Service worker for offline capability (optional)
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('/static/sw.js')
            .then(registration => console.log('SW registered'))
            .catch(error => console.log('SW registration failed'));
    });
}
