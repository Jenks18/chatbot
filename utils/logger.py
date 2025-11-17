"""
Enterprise-level logging utility
Provides structured logging with correlation IDs and context
"""
import logging
import json
import sys
from datetime import datetime
from typing import Any, Dict, Optional
import uuid

class StructuredLogger:
    """Structured JSON logger for enterprise monitoring"""
    
    def __init__(self, name: str = "kandih_toxwiki"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        
        # JSON formatter for structured logs
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(self.JsonFormatter())
        self.logger.addHandler(handler)
    
    class JsonFormatter(logging.Formatter):
        """Format logs as JSON for easy parsing"""
        
        def format(self, record: logging.LogRecord) -> str:
            log_data = {
                "timestamp": datetime.utcnow().isoformat(),
                "level": record.levelname,
                "logger": record.name,
                "message": record.getMessage(),
                "module": record.module,
                "function": record.funcName,
                "line": record.lineno,
            }
            
            # Add extra fields if present
            if hasattr(record, 'correlation_id'):
                log_data['correlation_id'] = record.correlation_id
            if hasattr(record, 'session_id'):
                log_data['session_id'] = record.session_id
            if hasattr(record, 'user_mode'):
                log_data['user_mode'] = record.user_mode
            if hasattr(record, 'response_time_ms'):
                log_data['response_time_ms'] = record.response_time_ms
            
            # Add exception info if present
            if record.exc_info:
                log_data['exception'] = self.formatException(record.exc_info)
            
            return json.dumps(log_data)
    
    def info(self, message: str, **kwargs):
        """Log info message with optional context"""
        extra = self._build_extra(**kwargs)
        self.logger.info(message, extra=extra)
    
    def error(self, message: str, **kwargs):
        """Log error message with optional context"""
        extra = self._build_extra(**kwargs)
        self.logger.error(message, extra=extra, exc_info=kwargs.get('exc_info', False))
    
    def warning(self, message: str, **kwargs):
        """Log warning message with optional context"""
        extra = self._build_extra(**kwargs)
        self.logger.warning(message, extra=extra)
    
    def debug(self, message: str, **kwargs):
        """Log debug message with optional context"""
        extra = self._build_extra(**kwargs)
        self.logger.debug(message, extra=extra)
    
    def _build_extra(self, **kwargs) -> Dict[str, Any]:
        """Build extra fields dict for logging"""
        extra = {}
        if 'correlation_id' in kwargs:
            extra['correlation_id'] = kwargs['correlation_id']
        if 'session_id' in kwargs:
            extra['session_id'] = kwargs['session_id']
        if 'user_mode' in kwargs:
            extra['user_mode'] = kwargs['user_mode']
        if 'response_time_ms' in kwargs:
            extra['response_time_ms'] = kwargs['response_time_ms']
        return extra


# Global logger instance
logger = StructuredLogger()


def generate_correlation_id() -> str:
    """Generate unique correlation ID for request tracking"""
    return str(uuid.uuid4())
