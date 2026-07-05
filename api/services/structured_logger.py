"""
Structured Logger - Phase 5.2
JSON-based structured logging with correlation IDs
"""

import json
import logging
import uuid
from typing import Any, Dict, Optional
from datetime import datetime
from enum import Enum
import contextvars

# Context variable for request correlation ID
correlation_id_var = contextvars.ContextVar('correlation_id', default=None)


class LogLevel(str, Enum):
    """Log levels"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class LogEntry:
    """Structured log entry"""

    def __init__(
        self,
        level: LogLevel,
        message: str,
        service: str = "codepulse",
        context: Optional[Dict[str, Any]] = None
    ):
        self.timestamp = datetime.utcnow().isoformat() + "Z"
        self.level = level.value
        self.message = message
        self.service = service
        self.correlation_id = correlation_id_var.get()
        self.context = context or {}

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "timestamp": self.timestamp,
            "level": self.level,
            "message": self.message,
            "service": self.service,
            "correlation_id": self.correlation_id,
            **self.context
        }

    def to_json(self) -> str:
        """Convert to JSON"""
        return json.dumps(self.to_dict())


class StructuredLogger:
    """Structured JSON logger"""

    def __init__(self, name: str, service: str = "codepulse"):
        self.name = name
        self.service = service
        self.logger = logging.getLogger(name)

    def set_correlation_id(self, correlation_id: Optional[str] = None) -> str:
        """Set correlation ID for request tracking"""
        if correlation_id is None:
            correlation_id = str(uuid.uuid4())

        correlation_id_var.set(correlation_id)
        return correlation_id

    def get_correlation_id(self) -> Optional[str]:
        """Get current correlation ID"""
        return correlation_id_var.get()

    def debug(self, message: str, **context) -> None:
        """Log debug message"""
        entry = LogEntry(LogLevel.DEBUG, message, self.service, context)
        self.logger.debug(entry.to_json())

    def info(self, message: str, **context) -> None:
        """Log info message"""
        entry = LogEntry(LogLevel.INFO, message, self.service, context)
        self.logger.info(entry.to_json())

    def warning(self, message: str, **context) -> None:
        """Log warning message"""
        entry = LogEntry(LogLevel.WARNING, message, self.service, context)
        self.logger.warning(entry.to_json())

    def error(self, message: str, exception: Optional[Exception] = None, **context) -> None:
        """Log error message"""
        if exception:
            context["exception"] = str(exception)
            context["exception_type"] = type(exception).__name__

        entry = LogEntry(LogLevel.ERROR, message, self.service, context)
        self.logger.error(entry.to_json())

    def critical(self, message: str, exception: Optional[Exception] = None, **context) -> None:
        """Log critical message"""
        if exception:
            context["exception"] = str(exception)
            context["exception_type"] = type(exception).__name__

        entry = LogEntry(LogLevel.CRITICAL, message, self.service, context)
        self.logger.critical(entry.to_json())

    def log_request(
        self,
        method: str,
        path: str,
        status_code: int = None,
        duration_ms: float = None,
        **context
    ) -> None:
        """Log API request"""
        self.info(
            f"API request: {method} {path}",
            method=method,
            path=path,
            status_code=status_code,
            duration_ms=duration_ms,
            **context
        )

    def log_agent_execution(
        self,
        agent_name: str,
        status: str,
        duration_ms: float,
        **context
    ) -> None:
        """Log agent execution"""
        self.info(
            f"Agent execution: {agent_name}",
            agent=agent_name,
            status=status,
            duration_ms=duration_ms,
            **context
        )

    def log_pipeline_start(self, pipeline_id: str, **context) -> None:
        """Log pipeline start"""
        self.info(
            f"Pipeline started: {pipeline_id}",
            pipeline_id=pipeline_id,
            event="pipeline_start",
            **context
        )

    def log_pipeline_complete(
        self,
        pipeline_id: str,
        status: str,
        duration_ms: float,
        **context
    ) -> None:
        """Log pipeline completion"""
        self.info(
            f"Pipeline completed: {pipeline_id}",
            pipeline_id=pipeline_id,
            status=status,
            duration_ms=duration_ms,
            event="pipeline_complete",
            **context
        )


class LogContextManager:
    """Context manager for logging with correlation ID"""

    def __init__(self, logger: StructuredLogger, correlation_id: Optional[str] = None):
        self.logger = logger
        self.correlation_id = correlation_id or str(uuid.uuid4())
        self.previous_id = None

    def __enter__(self):
        """Enter context"""
        self.previous_id = correlation_id_var.get()
        correlation_id_var.set(self.correlation_id)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context"""
        if self.previous_id:
            correlation_id_var.set(self.previous_id)
        else:
            correlation_id_var.set(None)

        if exc_type:
            self.logger.error(
                f"Context error: {exc_val}",
                exception=exc_val,
                correlation_id=self.correlation_id
            )


# Global logger registry
_loggers: Dict[str, StructuredLogger] = {}


def get_logger(name: str, service: str = "codepulse") -> StructuredLogger:
    """Get or create logger"""
    if name not in _loggers:
        _loggers[name] = StructuredLogger(name, service)

    return _loggers[name]


# Configure logging
def setup_structured_logging(level: str = "INFO") -> None:
    """Setup structured logging"""
    logging.basicConfig(
        format="%(message)s",
        level=getattr(logging, level)
    )

    # Suppress other loggers
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)


# Default logger
default_logger = get_logger("codepulse")
