import os
import logging
from pathlib import Path
from typing import Any, Optional, Dict, Union
from datetime import datetime
import json
import sqlite3
import threading
import time
import traceback
from functools import wraps
import re

# Create logs dir if not exists
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

# Set up logger
logger = logging.getLogger("zackgpt")
logger.setLevel(logging.DEBUG)  # Set to INFO or WARNING for production

# File handler for all logs
all_handler = logging.FileHandler(log_dir / "all.log")
all_handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))

# File handler for errors only
error_handler = logging.FileHandler(log_dir / "error.log")
error_handler.setLevel(logging.ERROR)
error_handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s\n%(pathname)s:%(lineno)d\n%(message)s"))

# Console handler with colors
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))

# Avoid adding duplicate handlers
if not logger.hasHandlers():
    logger.addHandler(all_handler)
    logger.addHandler(error_handler)
    logger.addHandler(console_handler)

# Quick aliases
log_debug = logger.debug
log_info = logger.info
log_warn = logger.warning
log_error = logger.error

# Get DEBUG_MODE from environment
DEBUG_MODE = os.getenv("DEBUG_MODE", "False").lower() == "true"

# Log aggregation settings
LOG_AGGREGATION_ENABLED = os.getenv("LOG_AGGREGATION_ENABLED", "true").lower() == "true"
LOG_DB_PATH = os.getenv("LOG_DB_PATH", "logs/zackgpt_analytics.db")

class LogError(Exception):
    """Custom exception for logging errors"""
    pass

class PerformanceMetrics:
    """Track and log performance metrics."""
    
    def __init__(self):
        self._metrics = {}
        self._lock = threading.Lock()
    
    def start_timer(self, operation: str) -> None:
        """Start timing an operation."""
        try:
            with self._lock:
                self._metrics[operation] = {
                    'start_time': time.time(),
                    'end_time': None,
                    'duration': None
                }
        except Exception as e:
            logger.error(f"Failed to start timer for {operation}: {str(e)}")
            raise LogError(f"Timer start failed: {str(e)}")
    
    def end_timer(self, operation: str) -> float:
        """End timing an operation and return duration."""
        try:
            with self._lock:
                if operation not in self._metrics:
                    raise LogError(f"No timer found for operation: {operation}")
                
                end_time = time.time()
                self._metrics[operation]['end_time'] = end_time
                duration = end_time - self._metrics[operation]['start_time']
                self._metrics[operation]['duration'] = duration
                
                logger.debug(f"Operation {operation} completed in {duration:.2f} seconds")
                return duration
        except Exception as e:
            logger.error(f"Failed to end timer for {operation}: {str(e)}")
            raise LogError(f"Timer end failed: {str(e)}")

# Global performance metrics instance
_perf_metrics = PerformanceMetrics()

def log_performance(operation: str):
    """Decorator to log performance of functions."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            _perf_metrics.start_timer(operation)
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                _perf_metrics.end_timer(operation)
        return wrapper
    return decorator

class LogAggregator:
    """Structured log aggregation for intelligent analysis."""
    
    def __init__(self, db_path: str = LOG_DB_PATH):
        self.db_path = db_path
        self.db_lock = threading.Lock()
        self._init_database()
    
    def _init_database(self):
        """Initialize SQLite database for log storage."""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS learning_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    component_name TEXT,
                    component_type TEXT,
                    user_rating INTEGER,
                    weight_before REAL,
                    weight_after REAL,
                    success_rate_before REAL,
                    success_rate_after REAL,
                    selection_probability REAL,
                    strategy TEXT,
                    context_type TEXT,
                    raw_data TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS system_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    level TEXT NOT NULL,
                    message TEXT,
                    data TEXT,
                    stack_trace TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS performance_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    operation TEXT NOT NULL,
                    duration REAL NOT NULL,
                    success BOOLEAN,
                    error_message TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Indexes for fast querying
            conn.execute("CREATE INDEX IF NOT EXISTS idx_learning_timestamp ON learning_events(timestamp)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_learning_component ON learning_events(component_name)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_learning_rating ON learning_events(user_rating)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_system_level ON system_events(level)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_performance_operation ON performance_metrics(operation)")
    
    def log_learning_event(self, event_type: str, component_name: str = None, **kwargs):
        """Log a learning-related event for analysis."""
        if not LOG_AGGREGATION_ENABLED:
            return
            
        with self.db_lock:
            try:
                with sqlite3.connect(self.db_path) as conn:
                    conn.execute("""
                        INSERT INTO learning_events (
                            timestamp, event_type, component_name, component_type,
                            user_rating, weight_before, weight_after, 
                            success_rate_before, success_rate_after,
                            selection_probability, strategy, context_type, raw_data
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        datetime.now().isoformat(),
                        event_type,
                        component_name,
                        kwargs.get('component_type'),
                        kwargs.get('user_rating'),
                        kwargs.get('weight_before'),
                        kwargs.get('weight_after'),
                        kwargs.get('success_rate_before'),
                        kwargs.get('success_rate_after'),
                        kwargs.get('selection_probability'),
                        kwargs.get('strategy'),
                        kwargs.get('context_type'),
                        json.dumps(kwargs)
                    ))
            except Exception as e:
                print(f"❌ Log aggregation error: {e}")
    
    def log_system_event(self, level: str, event_type: str, message: str, data: Dict = None, error: Exception = None):
        """Log a system event with optional error details."""
        if not LOG_AGGREGATION_ENABLED:
            return
            
        with self.db_lock:
            try:
                with sqlite3.connect(self.db_path) as conn:
                    conn.execute("""
                        INSERT INTO system_events (timestamp, event_type, level, message, data, stack_trace)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (
                        datetime.now().isoformat(),
                        event_type,
                        level,
                        message,
                        json.dumps(data) if data else None,
                        traceback.format_exc() if error else None
                    ))
            except Exception as e:
                print(f"❌ Log aggregation error: {e}")
    
    def log_performance(self, operation: str, duration: float, success: bool = True, error_message: str = None):
        """Log performance metrics."""
        if not LOG_AGGREGATION_ENABLED:
            return
            
        with self.db_lock:
            try:
                with sqlite3.connect(self.db_path) as conn:
                    conn.execute("""
                        INSERT INTO performance_metrics (timestamp, operation, duration, success, error_message)
                        VALUES (?, ?, ?, ?, ?)
                    """, (
                        datetime.now().isoformat(),
                        operation,
                        duration,
                        success,
                        error_message
                    ))
            except Exception as e:
                print(f"❌ Log aggregation error: {e}")

# Global log aggregator instance
_log_aggregator = LogAggregator() if LOG_AGGREGATION_ENABLED else None

def _sanitize_sensitive_data(data: Any) -> Any:
    """Sanitize sensitive data before logging."""
    if isinstance(data, str):
        # Hide API keys
        if "sk-" in data:
            return "sk-***"
        # Hide proxy information
        if any(x in data.lower() for x in ["proxy", "http_proxy", "https_proxy"]):
            return "***"
    elif isinstance(data, dict):
        return {k: _sanitize_sensitive_data(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [_sanitize_sensitive_data(item) for item in data]
    return data

def debug_log(message: str, data: Optional[Any] = None, prefix: str = "🔍") -> None:
    """
    Log debug messages only when DEBUG_MODE is enabled.
    Includes structured aggregation for analysis.
    Args:
        message: The debug message to log
        data: Optional data to log (will be formatted as JSON if dict/list)
        prefix: Optional emoji prefix for the message
    """
    if not DEBUG_MODE:
        return
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    output = f"{prefix} [{timestamp}] {message}"
    if data is not None:
        sanitized_data = _sanitize_sensitive_data(data)
        if isinstance(sanitized_data, (dict, list)):
            output += f"\n{json.dumps(sanitized_data, indent=2)}"
        else:
            output += f"\n{sanitized_data}"
    print(output)
    
    # Aggregate for analysis
    if _log_aggregator:
        _log_aggregator.log_system_event("DEBUG", "debug_log", message, data)

def debug_error(message: str, error: Optional[Exception] = None) -> None:
    """Log error messages with optional exception details."""
    if not DEBUG_MODE:
        return
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    output = f"❌ [{timestamp}] {message}"
    if error:
        output += f"\nError details: {str(error)}"
        output += f"\nStack trace:\n{traceback.format_exc()}"
    print(output)
    
    error_data = {"error": str(error)} if error else None
    if _log_aggregator:
        _log_aggregator.log_system_event("ERROR", "error", message, error_data, error)

def debug_success(message: str, data: Optional[Any] = None) -> None:
    """Log success messages with optional data."""
    if not DEBUG_MODE:
        return
    debug_log(message, data, prefix="✅")
    
    if _log_aggregator:
        _log_aggregator.log_system_event("SUCCESS", "success", message, data)

def debug_warning(message: str, data: Optional[Any] = None) -> None:
    """Log warning messages with optional data."""
    if not DEBUG_MODE:
        return
    debug_log(message, data, prefix="⚠️")
    
    if _log_aggregator:
        _log_aggregator.log_system_event("WARNING", "warning", message, data)

def debug_info(message: str, data: Optional[Any] = None) -> None:
    """Log info messages with optional data."""
    if not DEBUG_MODE:
        return
    debug_log(message, data, prefix="ℹ️")
    
    if _log_aggregator:
        _log_aggregator.log_system_event("INFO", "info", message, data)

def log_learning_event(event_type: str, component_name: str = None, **kwargs):
    """Log learning events for analytics and debugging."""
    if _log_aggregator:
        _log_aggregator.log_learning_event(event_type, component_name, **kwargs)

def log_component_selection(component_name: str, component_type: str, selection_probability: float, **kwargs):
    """Log component selection for analysis."""
    log_learning_event(
        "component_selected",
        component_name=component_name,
        component_type=component_type,
        selection_probability=selection_probability,
        **kwargs
    )

def log_user_rating(rating: int, component_name: str, weight_before: float, weight_after: float, **kwargs):
    """Log user rating events for analysis."""
    log_learning_event(
        "user_rating",
        component_name=component_name,
        user_rating=rating,
        weight_before=weight_before,
        weight_after=weight_after,
        **kwargs
    )

def log_component_performance_update(component_name: str, success: bool, weight_before: float, weight_after: float, 
                                   success_rate_before: float, success_rate_after: float, **kwargs):
    """Log component performance updates."""
    log_learning_event(
        "performance_update",
        component_name=component_name,
        weight_before=weight_before,
        weight_after=weight_after,
        success_rate_before=success_rate_before,
        success_rate_after=success_rate_after,
        success=success,
        **kwargs
    )

def log_performance_metric(operation: str, duration: float, success: bool = True, error_message: str = None):
    """Log performance metrics for analysis."""
    if _log_aggregator:
        _log_aggregator.log_performance(operation, duration, success, error_message)

def log_performance_metrics(operation: str, duration: float, details: Optional[Dict] = None) -> None:
    """Log performance metrics for an operation"""
    try:
        metrics = {
            'operation': operation,
            'duration': duration,
            'timestamp': datetime.now().isoformat()
        }
        if details:
            metrics.update(details)
        
        debug_info(f"Performance metrics for {operation}", metrics)
        log_system_event('performance', f"Operation {operation} completed", metrics)
    except Exception as e:
        debug_error(f"Failed to log performance metrics for {operation}", e, {
            'duration': duration,
            'details': details
        })
        raise LogError(f"Performance metrics logging failed: {str(e)}")

def performance_logger(func):
    """Decorator to log performance metrics for a function"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            start_time = time.time()
            result = func(*args, **kwargs)
            duration = time.time() - start_time
            
            log_performance_metrics(
                func.__name__,
                duration,
                {
                    'args': str(args),
                    'kwargs': str(kwargs),
                    'result_type': type(result).__name__
                }
            )
            return result
        except Exception as e:
            debug_error(f"Performance logging failed for {func.__name__}", e)
            raise
    return wrapper
