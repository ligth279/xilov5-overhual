"""
Enhanced Logging System for Xilo AI Tutor
Provides detailed system state tracking and rollback information
"""

import os
import json
import time
import datetime
import logging
import traceback
import psutil
import threading
from functools import wraps
from typing import Dict, List, Any, Optional

class XiloLogger:
    def __init__(self, log_dir="logs"):
        self.log_dir = log_dir
        self.session_id = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        self.setup_directories()
        self.setup_logging()
        self.system_snapshots = []
        self.error_history = []
        self.performance_logs = []
        self.model_state_log = []
        
    def setup_directories(self):
        """Create logging directory structure"""
        os.makedirs(self.log_dir, exist_ok=True)
        os.makedirs(f"{self.log_dir}/system", exist_ok=True)
        os.makedirs(f"{self.log_dir}/errors", exist_ok=True)
        os.makedirs(f"{self.log_dir}/performance", exist_ok=True)
        os.makedirs(f"{self.log_dir}/model", exist_ok=True)
        
    def setup_logging(self):
        """Setup detailed logging configuration"""
        # Create formatters (without emojis for Windows compatibility)
        detailed_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
        )
        
        simple_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )
        
        # Main application log
        self.main_logger = logging.getLogger('xilo_main')
        self.main_logger.setLevel(logging.DEBUG)
        
        # File handlers
        main_handler = logging.FileHandler(
            f"{self.log_dir}/xilo_main_{self.session_id}.log",
            encoding='utf-8'
        )
        main_handler.setFormatter(detailed_formatter)
        self.main_logger.addHandler(main_handler)
        
        # System log
        self.system_logger = logging.getLogger('xilo_system')
        system_handler = logging.FileHandler(
            f"{self.log_dir}/system/system_{self.session_id}.log",
            encoding='utf-8'
        )
        system_handler.setFormatter(detailed_formatter)
        self.system_logger.addHandler(system_handler)
        
        # Error log
        self.error_logger = logging.getLogger('xilo_errors')
        error_handler = logging.FileHandler(
            f"{self.log_dir}/errors/errors_{self.session_id}.log",
            encoding='utf-8'
        )
        error_handler.setFormatter(detailed_formatter)
        self.error_logger.addHandler(error_handler)
        
        # Performance log
        self.perf_logger = logging.getLogger('xilo_performance')
        perf_handler = logging.FileHandler(
            f"{self.log_dir}/performance/perf_{self.session_id}.log",
            encoding='utf-8'
        )
        perf_handler.setFormatter(simple_formatter)
        self.perf_logger.addHandler(perf_handler)
        
        # Model state log
        self.model_logger = logging.getLogger('xilo_model')
        model_handler = logging.FileHandler(
            f"{self.log_dir}/model/model_{self.session_id}.log",
            encoding='utf-8'
        )
        model_handler.setFormatter(detailed_formatter)
        self.model_logger.addHandler(model_handler)
        
    def log_system_snapshot(self, checkpoint_name: str = None):
        """Take a detailed system snapshot"""
        try:
            import torch
            
            snapshot = {
                'timestamp': datetime.datetime.now().isoformat(),
                'checkpoint_name': checkpoint_name or f"snapshot_{len(self.system_snapshots)}",
                'system': {
                    'cpu_percent': psutil.cpu_percent(),
                    'memory': dict(psutil.virtual_memory()._asdict()),
                    'disk': dict(psutil.disk_usage('/')._asdict()) if os.name != 'nt' else dict(psutil.disk_usage('C:')._asdict()),
                    'python_version': f"{psutil.sys.version_info.major}.{psutil.sys.version_info.minor}.{psutil.sys.version_info.micro}",
                },
                'pytorch': {
                    'version': torch.__version__,
                    'cuda_available': torch.cuda.is_available() if hasattr(torch, 'cuda') else False,
                    'xpu_available': torch.xpu.is_available() if hasattr(torch, 'xpu') else False,
                }
            }
            
            # Add Intel GPU specific info
            if hasattr(torch, 'xpu') and torch.xpu.is_available():
                try:
                    snapshot['intel_gpu'] = {
                        'device_count': torch.xpu.device_count(),
                        'current_device': torch.xpu.current_device(),
                        'device_name': torch.xpu.get_device_name(torch.xpu.current_device()),
                        'memory_allocated': torch.xpu.memory_allocated(),
                        'memory_reserved': torch.xpu.memory_reserved(),
                    }
                except Exception as e:
                    snapshot['intel_gpu_error'] = str(e)
                    
            # Add process info
            process = psutil.Process()
            snapshot['process'] = {
                'pid': process.pid,
                'cpu_percent': process.cpu_percent(),
                'memory_info': dict(process.memory_info()._asdict()),
                'num_threads': process.num_threads(),
                'create_time': process.create_time(),
            }
            
            self.system_snapshots.append(snapshot)
            
            # Save to file
            snapshot_file = f"{self.log_dir}/system/snapshot_{self.session_id}_{len(self.system_snapshots)}.json"
            with open(snapshot_file, 'w', encoding='utf-8') as f:
                json.dump(snapshot, f, indent=2, default=str)
                
            self.system_logger.info(f"System snapshot saved: {checkpoint_name}")
            return snapshot
            
        except Exception as e:
            self.error_logger.error(f"Failed to create system snapshot: {e}")
            return None
    
    def log_error(self, error: Exception, context: str = None, rollback_info: Dict = None):
        """Log detailed error information"""
        try:
            error_entry = {
                'timestamp': datetime.datetime.now().isoformat(),
                'error_type': type(error).__name__,
                'error_message': str(error),
                'context': context,
                'traceback': traceback.format_exc(),
                'rollback_info': rollback_info,
                'system_state': self.get_current_system_state()
            }
            
            self.error_history.append(error_entry)
            
            # Save to file
            error_file = f"{self.log_dir}/errors/error_{self.session_id}_{len(self.error_history)}.json"
            with open(error_file, 'w', encoding='utf-8') as f:
                json.dump(error_entry, f, indent=2, default=str)
                
            self.error_logger.error(f"Error logged: {type(error).__name__} - {error}")
            
            return error_entry
            
        except Exception as e:
            print(f"Failed to log error: {e}")
    
    def log_performance(self, operation: str, duration: float, details: Dict = None):
        """Log performance metrics"""
        try:
            perf_entry = {
                'timestamp': datetime.datetime.now().isoformat(),
                'operation': operation,
                'duration_seconds': duration,
                'details': details or {}
            }
            
            self.performance_logs.append(perf_entry)
            self.perf_logger.info(f"{operation}: {duration:.3f}s")
            
            # Save detailed performance data
            if len(self.performance_logs) % 10 == 0:  # Save every 10 entries
                perf_file = f"{self.log_dir}/performance/performance_{self.session_id}.json"
                with open(perf_file, 'w', encoding='utf-8') as f:
                    json.dump(self.performance_logs, f, indent=2, default=str)
                    
        except Exception as e:
            print(f"Failed to log performance: {e}")
    
    def log_model_state(self, state: str, details: Dict = None):
        """Log model loading and state changes"""
        try:
            model_entry = {
                'timestamp': datetime.datetime.now().isoformat(),
                'state': state,
                'details': details or {}
            }
            
            self.model_state_log.append(model_entry)
            self.model_logger.info(f"Model state: {state}")
            
            # Save model state
            model_file = f"{self.log_dir}/model/model_states_{self.session_id}.json"
            with open(model_file, 'w', encoding='utf-8') as f:
                json.dump(self.model_state_log, f, indent=2, default=str)
                
        except Exception as e:
            print(f"Failed to log model state: {e}")
    
    def get_current_system_state(self):
        """Get current system state for rollback purposes"""
        try:
            import torch
            
            state = {
                'timestamp': datetime.datetime.now().isoformat(),
                'cpu_percent': psutil.cpu_percent(),
                'memory_percent': psutil.virtual_memory().percent,
                'pytorch_version': torch.__version__,
                'xpu_available': torch.xpu.is_available() if hasattr(torch, 'xpu') else False,
            }
            
            if hasattr(torch, 'xpu') and torch.xpu.is_available():
                try:
                    state['xpu_memory_allocated'] = torch.xpu.memory_allocated()
                    state['xpu_memory_reserved'] = torch.xpu.memory_reserved()
                except:
                    pass
                    
            return state
            
        except Exception as e:
            return {'error': str(e), 'timestamp': datetime.datetime.now().isoformat()}
    
    def generate_rollback_guide(self) -> str:
        """Generate a rollback guide based on logged information"""
        try:
            guide = f"""
# Xilo AI Tutor - Rollback Guide
Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Session ID: {self.session_id}

## System Snapshots
"""
            for i, snapshot in enumerate(self.system_snapshots):
                guide += f"""
### Snapshot {i+1}: {snapshot.get('checkpoint_name', 'Unknown')}
- Timestamp: {snapshot['timestamp']}
- CPU Usage: {snapshot['system']['cpu_percent']}%
- Memory Usage: {snapshot['system']['memory']['percent']}%
- XPU Available: {snapshot['pytorch'].get('xpu_available', 'Unknown')}
"""

            guide += f"""

## Error History ({len(self.error_history)} errors)
"""
            for i, error in enumerate(self.error_history[-5:]):  # Last 5 errors
                guide += f"""
### Error {i+1}: {error['error_type']}
- Time: {error['timestamp']}
- Message: {error['error_message']}
- Context: {error.get('context', 'N/A')}
"""

            guide += f"""

## Performance Issues
"""
            slow_operations = [p for p in self.performance_logs if p['duration_seconds'] > 10]
            for op in slow_operations[-5:]:  # Last 5 slow operations
                guide += f"""
- {op['operation']}: {op['duration_seconds']:.2f}s at {op['timestamp']}
"""

            guide += f"""

## Model State Changes
"""
            for state in self.model_state_log[-10:]:  # Last 10 state changes
                guide += f"""
- {state['timestamp']}: {state['state']}
"""

            guide += f"""

## Rollback Steps

### 1. Stop Current Session
```bash
# Stop the Flask server (Ctrl+C in terminal)
# Or kill the process if unresponsive
```

### 2. Check System State
```bash
# Check GPU status
python test_setup.py

# Check disk space
dir "models_cache"

# Check memory usage
```

### 3. Clean Restart Options

#### Option A: Quick Restart
```bash
# Just restart the application
python app.py
```

#### Option B: Clear Model Cache
```bash
# Remove model cache if corrupted
rmdir /s "models_cache"
python app.py
```

#### Option C: Full Reset
```bash
# Reset virtual environment
deactivate
rmdir /s ".venv"
python -m venv .venv
.venv\\Scripts\\activate
pip install -r requirements.txt
python app.py
```

### 4. Recovery Commands
```bash
# Check Intel GPU drivers
dxdiag

# Update PyTorch XPU
pip install --upgrade torch torchvision torchaudio --index-url https://download.pytorch.org/whl/xpu
pip install --upgrade intel-extension-for-pytorch --extra-index-url https://pytorch-extension.intel.com/release-whl/stable/xpu/us/

# Check system resources
python -c "import psutil; print(f'CPU: {{psutil.cpu_percent()}}%, Memory: {{psutil.virtual_memory().percent}}%')"
```

## Log Files Locations
- Main logs: {self.log_dir}/
- System snapshots: {self.log_dir}/system/
- Error details: {self.log_dir}/errors/
- Performance data: {self.log_dir}/performance/
- Model states: {self.log_dir}/model/

## Contact Information
If issues persist:
1. Check the error logs in {self.log_dir}/errors/
2. Review system snapshots for resource issues
3. Verify Intel GPU driver installation
4. Check model download integrity
"""

            return guide
            
        except Exception as e:
            return f"Failed to generate rollback guide: {e}"
    
    def save_rollback_guide(self):
        """Save the rollback guide to a file"""
        try:
            guide = self.generate_rollback_guide()
            guide_file = f"{self.log_dir}/ROLLBACK_GUIDE_{self.session_id}.md"
            
            with open(guide_file, 'w', encoding='utf-8') as f:
                f.write(guide)
                
            self.main_logger.info(f"Rollback guide saved: {guide_file}")
            return guide_file
            
        except Exception as e:
            print(f"Failed to save rollback guide: {e}")
            return None

# Performance monitoring decorator
def monitor_performance(logger_instance, operation_name):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                logger_instance.log_performance(operation_name, duration, {
                    'success': True,
                    'args_count': len(args),
                    'kwargs_count': len(kwargs)
                })
                return result
            except Exception as e:
                duration = time.time() - start_time
                logger_instance.log_performance(operation_name, duration, {
                    'success': False,
                    'error': str(e)
                })
                logger_instance.log_error(e, f"Performance monitoring: {operation_name}")
                raise
        return wrapper
    return decorator

# Global logger instance
xilo_logger = XiloLogger()
