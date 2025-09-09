// Xilo AI Tutor - Logs & Diagnostics JavaScript

class LogsManager {
    constructor() {
        this.refreshInterval = 5000; // 5 seconds
        this.autoRefresh = true;
        this.init();
    }
    
    init() {
        this.loadInitialData();
        this.startAutoRefresh();
        console.log('📊 Logs Manager initialized');
    }
    
    async loadInitialData() {
        try {
            await Promise.all([
                this.updateSystemStats(),
                this.updateErrorStats(),
                this.updatePerformanceStats(),
                this.updateModelStats()
            ]);
        } catch (error) {
            console.error('Error loading initial data:', error);
        }
    }
    
    async updateSystemStats() {
        try {
            const response = await fetch('/api/logs/system');
            const data = await response.json();
            
            if (data.status === 'success') {
                const currentState = data.data.current_state;
                
                document.getElementById('cpu-usage').textContent = 
                    currentState.cpu_percent ? `${currentState.cpu_percent.toFixed(1)}` : '--';
                
                document.getElementById('memory-usage').textContent = 
                    currentState.memory_percent ? `${currentState.memory_percent.toFixed(1)}` : '--';
                
                const gpuStatus = currentState.xpu_available ? 'Active' : 'Inactive';
                const gpuElement = document.getElementById('gpu-status');
                gpuElement.textContent = gpuStatus;
                gpuElement.className = currentState.xpu_available ? 'stat-number' : 'stat-number status-warning';
            }
        } catch (error) {
            console.error('Error updating system stats:', error);
        }
    }
    
    async updateErrorStats() {
        try {
            const response = await fetch('/api/logs/errors');
            const data = await response.json();
            
            if (data.status === 'success') {
                document.getElementById('total-errors').textContent = data.data.total_errors;
                document.getElementById('recent-errors').textContent = data.data.recent_errors.length;
            }
        } catch (error) {
            console.error('Error updating error stats:', error);
        }
    }
    
    async updatePerformanceStats() {
        try {
            const response = await fetch('/api/logs/performance');
            const data = await response.json();
            
            if (data.status === 'success') {
                const stats = data.data.stats;
                document.getElementById('avg-response').textContent = 
                    stats.average_duration ? stats.average_duration.toFixed(2) : '--';
                document.getElementById('total-operations').textContent = stats.total_operations;
            }
        } catch (error) {
            console.error('Error updating performance stats:', error);
        }
    }
    
    async updateModelStats() {
        try {
            const response = await fetch('/api/logs/model');
            const data = await response.json();
            
            if (data.status === 'success') {
                const currentStatus = data.data.current_status;
                const stateChanges = data.data.model_states.length;
                
                let statusText = 'Unknown';
                if (currentStatus.is_loaded) {
                    statusText = 'Loaded';
                } else if (currentStatus.is_loading) {
                    statusText = 'Loading';
                } else if (currentStatus.error) {
                    statusText = 'Error';
                }
                
                document.getElementById('model-state').textContent = statusText;
                document.getElementById('state-changes').textContent = stateChanges;
            }
        } catch (error) {
            console.error('Error updating model stats:', error);
        }
    }
    
    startAutoRefresh() {
        if (this.autoRefresh) {
            setInterval(() => {
                this.loadInitialData();
            }, this.refreshInterval);
        }
    }
    
    showLogDetails(title, content) {
        const detailsSection = document.getElementById('log-details');
        const detailsTitle = document.getElementById('log-details-title');
        const detailsContent = document.getElementById('log-details-content');
        
        detailsTitle.textContent = title;
        detailsContent.innerHTML = content;
        detailsSection.style.display = 'block';
        
        // Scroll to details
        detailsSection.scrollIntoView({ behavior: 'smooth' });
    }
    
    formatLogEntry(entry, type = 'generic') {
        const timestamp = new Date(entry.timestamp).toLocaleString();
        
        switch (type) {
            case 'error':
                return `
                    <div class="log-entry">
                        <div class="log-timestamp">${timestamp}</div>
                        <div class="log-level-error">ERROR: ${entry.error_type}</div>
                        <div>${entry.error_message}</div>
                        ${entry.context ? `<div><strong>Context:</strong> ${entry.context}</div>` : ''}
                        ${entry.rollback_info ? `<div><strong>Recovery:</strong> ${entry.rollback_info.suggested_rollback}</div>` : ''}
                    </div>
                `;
            case 'performance':
                return `
                    <div class="log-entry">
                        <div class="log-timestamp">${timestamp}</div>
                        <div class="log-level-info">${entry.operation}</div>
                        <div>Duration: ${entry.duration_seconds.toFixed(3)}s</div>
                        ${entry.details ? `<div>Details: ${JSON.stringify(entry.details, null, 2)}</div>` : ''}
                    </div>
                `;
            case 'system':
                return `
                    <div class="log-entry">
                        <div class="log-timestamp">${timestamp}</div>
                        <div class="log-level-info">${entry.checkpoint_name}</div>
                        <div>CPU: ${entry.system?.cpu_percent}%, Memory: ${entry.system?.memory?.percent}%</div>
                        ${entry.intel_gpu ? `<div>GPU: ${entry.intel_gpu.device_name}</div>` : ''}
                    </div>
                `;
            case 'model':
                return `
                    <div class="log-entry">
                        <div class="log-timestamp">${timestamp}</div>
                        <div class="log-level-info">STATE: ${entry.state}</div>
                        ${entry.details ? `<div>${JSON.stringify(entry.details, null, 2)}</div>` : ''}
                    </div>
                `;
            default:
                return `
                    <div class="log-entry">
                        <div class="log-timestamp">${timestamp}</div>
                        <div>${JSON.stringify(entry, null, 2)}</div>
                    </div>
                `;
        }
    }
}

// Log viewing functions
async function viewSystemLogs() {
    try {
        const response = await fetch('/api/logs/system');
        const data = await response.json();
        
        if (data.status === 'success') {
            let content = '<h4>Recent System Snapshots</h4>';
            
            data.data.recent_snapshots.forEach(snapshot => {
                content += logsManager.formatLogEntry(snapshot, 'system');
            });
            
            content += `<h4>Current State</h4>`;
            content += `
                <div class="log-entry">
                    <div class="log-timestamp">${new Date().toLocaleString()}</div>
                    <div class="log-level-info">CURRENT STATE</div>
                    <div>CPU: ${data.data.current_state.cpu_percent}%</div>
                    <div>Memory: ${data.data.current_state.memory_percent}%</div>
                    <div>GPU Available: ${data.data.current_state.xpu_available ? 'Yes' : 'No'}</div>
                    <div>PyTorch: ${data.data.current_state.pytorch_version}</div>
                </div>
            `;
            
            logsManager.showLogDetails('System Logs', content);
        }
    } catch (error) {
        console.error('Error viewing system logs:', error);
        logsManager.showLogDetails('System Logs', '<div class="log-entry status-error">Failed to load system logs</div>');
    }
}

async function viewErrorLogs() {
    try {
        const response = await fetch('/api/logs/errors');
        const data = await response.json();
        
        if (data.status === 'success') {
            let content = `<h4>Recent Errors (${data.data.total_errors} total)</h4>`;
            
            if (data.data.recent_errors.length === 0) {
                content += '<div class="log-entry status-success">No recent errors found! 🎉</div>';
            } else {
                data.data.recent_errors.forEach(error => {
                    content += logsManager.formatLogEntry(error, 'error');
                });
            }
            
            logsManager.showLogDetails('Error Logs', content);
        }
    } catch (error) {
        console.error('Error viewing error logs:', error);
        logsManager.showLogDetails('Error Logs', '<div class="log-entry status-error">Failed to load error logs</div>');
    }
}

async function viewPerformanceLogs() {
    try {
        const response = await fetch('/api/logs/performance');
        const data = await response.json();
        
        if (data.status === 'success') {
            const stats = data.data.stats;
            let content = `
                <h4>Performance Statistics</h4>
                <div class="log-stats">
                    <div class="stat-item">
                        <div class="stat-number">${stats.total_operations}</div>
                        <div class="stat-label">Total Operations</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-number">${stats.average_duration.toFixed(3)}s</div>
                        <div class="stat-label">Average Duration</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-number">${stats.max_duration.toFixed(3)}s</div>
                        <div class="stat-label">Max Duration</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-number">${stats.min_duration.toFixed(3)}s</div>
                        <div class="stat-label">Min Duration</div>
                    </div>
                </div>
                <h4>Recent Operations</h4>
            `;
            
            data.data.recent_operations.forEach(op => {
                content += logsManager.formatLogEntry(op, 'performance');
            });
            
            logsManager.showLogDetails('Performance Logs', content);
        }
    } catch (error) {
        console.error('Error viewing performance logs:', error);
        logsManager.showLogDetails('Performance Logs', '<div class="log-entry status-error">Failed to load performance logs</div>');
    }
}

async function viewModelLogs() {
    try {
        const response = await fetch('/api/logs/model');
        const data = await response.json();
        
        if (data.status === 'success') {
            let content = `
                <h4>Current Model Status</h4>
                <div class="log-entry">
                    <div class="log-timestamp">${new Date().toLocaleString()}</div>
                    <div class="log-level-info">STATUS</div>
                    <div>Is Loading: ${data.data.current_status.is_loading ? 'Yes' : 'No'}</div>
                    <div>Is Loaded: ${data.data.current_status.is_loaded ? 'Yes' : 'No'}</div>
                    ${data.data.current_status.error ? `<div class="log-level-error">Error: ${data.data.current_status.error}</div>` : ''}
                </div>
                <h4>Model State History</h4>
            `;
            
            data.data.model_states.slice(-10).forEach(state => {
                content += logsManager.formatLogEntry(state, 'model');
            });
            
            logsManager.showLogDetails('Model Logs', content);
        }
    } catch (error) {
        console.error('Error viewing model logs:', error);
        logsManager.showLogDetails('Model Logs', '<div class="log-entry status-error">Failed to load model logs</div>');
    }
}

// Emergency actions
async function generateRollbackGuide() {
    try {
        const response = await fetch('/api/rollback-guide');
        const data = await response.json();
        
        if (data.status === 'success') {
            // Create a downloadable file
            const blob = new Blob([data.data.guide], { type: 'text/markdown' });
            const url = URL.createObjectURL(blob);
            
            const a = document.createElement('a');
            a.href = url;
            a.download = `xilo-rollback-guide-${data.data.session_id}.md`;
            a.click();
            
            URL.revokeObjectURL(url);
            
            // Show preview
            const content = `
                <h4>Rollback Guide Generated</h4>
                <div class="log-entry status-success">
                    <div>✅ Guide generated and downloaded successfully!</div>
                    <div>Session ID: ${data.data.session_id}</div>
                    <div>File: xilo-rollback-guide-${data.data.session_id}.md</div>
                </div>
                <h4>Quick Preview</h4>
                <pre style="white-space: pre-wrap; background: var(--dark-bg); padding: 1rem; border-radius: 0.5rem; max-height: 400px; overflow-y: auto;">${data.data.guide.substring(0, 2000)}...</pre>
            `;
            
            logsManager.showLogDetails('Rollback Guide', content);
        } else {
            throw new Error(data.message);
        }
    } catch (error) {
        console.error('Error generating rollback guide:', error);
        logsManager.showLogDetails('Rollback Guide', `<div class="log-entry status-error">Failed to generate rollback guide: ${error.message}</div>`);
    }
}

async function clearGPUMemory() {
    try {
        const response = await fetch('/api/clear-memory', { method: 'POST' });
        const data = await response.json();
        
        if (data.status === 'success') {
            logsManager.showLogDetails('GPU Memory', '<div class="log-entry status-success">✅ GPU memory cleared successfully!</div>');
            // Refresh stats after clearing memory
            setTimeout(() => logsManager.updateSystemStats(), 1000);
        } else {
            throw new Error(data.message);
        }
    } catch (error) {
        console.error('Error clearing GPU memory:', error);
        logsManager.showLogDetails('GPU Memory', `<div class="log-entry status-error">Failed to clear GPU memory: ${error.message}</div>`);
    }
}

function downloadAllLogs() {
    const logTypes = ['main', 'system', 'errors', 'performance', 'model'];
    
    logTypes.forEach((logType, index) => {
        setTimeout(() => {
            const link = document.createElement('a');
            link.href = `/api/logs/download/${logType}`;
            link.download = `xilo-${logType}-logs.log`;
            link.click();
        }, index * 500); // Stagger downloads
    });
    
    logsManager.showLogDetails('Download All Logs', '<div class="log-entry status-success">✅ All log files are being downloaded...</div>');
}

function restartModel() {
    // This would typically trigger a model restart endpoint
    logsManager.showLogDetails('Restart Model', `
        <div class="log-entry status-warning">
            <div>⚠️ Model restart functionality</div>
            <div>To restart the model, please:</div>
            <div>1. Stop the current server (Ctrl+C)</div>
            <div>2. Run: python app.py</div>
            <div>3. Wait for model to reload</div>
        </div>
    `);
}

// Initialize logs manager when page loads
document.addEventListener('DOMContentLoaded', () => {
    window.logsManager = new LogsManager();
});

// Add refresh button functionality
function toggleAutoRefresh() {
    logsManager.autoRefresh = !logsManager.autoRefresh;
    if (logsManager.autoRefresh) {
        logsManager.startAutoRefresh();
    }
}

// Add keyboard shortcuts
document.addEventListener('keydown', (e) => {
    if (e.ctrlKey) {
        switch (e.key) {
            case 'r':
                e.preventDefault();
                logsManager.loadInitialData();
                break;
            case 's':
                e.preventDefault();
                viewSystemLogs();
                break;
            case 'e':
                e.preventDefault();
                viewErrorLogs();
                break;
            case 'p':
                e.preventDefault();
                viewPerformanceLogs();
                break;
            case 'm':
                e.preventDefault();
                viewModelLogs();
                break;
        }
    }
});

console.log(`
📊 Xilo Logs & Diagnostics Interface
Keyboard shortcuts:
- Ctrl+R: Refresh all data
- Ctrl+S: View system logs
- Ctrl+E: View error logs
- Ctrl+P: View performance logs
- Ctrl+M: View model logs
`);
