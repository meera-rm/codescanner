"""
Distributed Tracer - Phase 5.2
OpenTelemetry-style distributed tracing
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
import time
import uuid
import json
from datetime import datetime


class SpanKind(str, Enum):
    """Span kind types"""
    INTERNAL = "INTERNAL"
    SERVER = "SERVER"
    CLIENT = "CLIENT"
    PRODUCER = "PRODUCER"
    CONSUMER = "CONSUMER"


class SpanStatus(str, Enum):
    """Span status"""
    UNSET = "UNSET"
    OK = "OK"
    ERROR = "ERROR"


@dataclass
class SpanEvent:
    """Event within a span"""
    name: str
    timestamp: float
    attributes: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Span:
    """Distributed trace span"""
    trace_id: str
    span_id: str
    parent_span_id: Optional[str]
    operation_name: str
    kind: SpanKind
    start_time: float = field(default_factory=time.time)
    end_time: Optional[float] = None
    status: SpanStatus = SpanStatus.UNSET
    attributes: Dict[str, Any] = field(default_factory=dict)
    events: List[SpanEvent] = field(default_factory=list)

    def set_attribute(self, key: str, value: Any) -> None:
        """Set span attribute"""
        self.attributes[key] = value

    def add_event(self, name: str, attributes: Optional[Dict[str, Any]] = None) -> None:
        """Add event to span"""
        self.events.append(SpanEvent(
            name=name,
            timestamp=time.time(),
            attributes=attributes or {}
        ))

    def set_status(self, status: SpanStatus) -> None:
        """Set span status"""
        self.status = status

    def end(self) -> None:
        """End span"""
        self.end_time = time.time()

    def duration_ms(self) -> float:
        """Get span duration in milliseconds"""
        end = self.end_time or time.time()
        return (end - self.start_time) * 1000

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "trace_id": self.trace_id,
            "span_id": self.span_id,
            "parent_span_id": self.parent_span_id,
            "operation_name": self.operation_name,
            "kind": self.kind.value,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration_ms": self.duration_ms(),
            "status": self.status.value,
            "attributes": self.attributes,
            "events": [
                {
                    "name": e.name,
                    "timestamp": e.timestamp,
                    "attributes": e.attributes
                }
                for e in self.events
            ]
        }


class Tracer:
    """Distributed tracer"""

    def __init__(self):
        self.spans: Dict[str, Span] = {}
        self.trace_context = {}

    def start_trace(self, trace_id: Optional[str] = None) -> str:
        """Start new trace"""
        trace_id = trace_id or str(uuid.uuid4())
        self.trace_context["trace_id"] = trace_id
        return trace_id

    def start_span(
        self,
        operation_name: str,
        kind: SpanKind = SpanKind.INTERNAL,
        attributes: Optional[Dict[str, Any]] = None,
        parent_span_id: Optional[str] = None
    ) -> Span:
        """Start new span"""
        trace_id = self.trace_context.get("trace_id", str(uuid.uuid4()))
        span_id = str(uuid.uuid4())

        span = Span(
            trace_id=trace_id,
            span_id=span_id,
            parent_span_id=parent_span_id or self.trace_context.get("span_id"),
            operation_name=operation_name,
            kind=kind,
            attributes=attributes or {}
        )

        self.spans[span_id] = span
        self.trace_context["span_id"] = span_id

        return span

    def get_span(self, span_id: str) -> Optional[Span]:
        """Get span by ID"""
        return self.spans.get(span_id)

    def list_spans(self, trace_id: str) -> List[Span]:
        """List all spans in trace"""
        return [s for s in self.spans.values() if s.trace_id == trace_id]

    def export_spans(self, trace_id: str) -> str:
        """Export spans as JSON"""
        spans = self.list_spans(trace_id)
        return json.dumps([s.to_dict() for s in spans], indent=2)

    def get_trace_tree(self, trace_id: str) -> Dict[str, Any]:
        """Get trace as tree structure"""
        spans = self.list_spans(trace_id)

        # Build tree
        root_spans = [s for s in spans if s.parent_span_id is None]
        tree = {
            "trace_id": trace_id,
            "total_spans": len(spans),
            "total_duration_ms": sum(s.duration_ms() for s in spans),
            "spans": []
        }

        for root_span in root_spans:
            tree["spans"].append(self._build_span_tree(root_span, spans))

        return tree

    def _build_span_tree(self, span: Span, all_spans: List[Span]) -> Dict[str, Any]:
        """Build span tree recursively"""
        children = [s for s in all_spans if s.parent_span_id == span.span_id]

        return {
            "operation_name": span.operation_name,
            "kind": span.kind.value,
            "duration_ms": span.duration_ms(),
            "status": span.status.value,
            "children": [self._build_span_tree(child, all_spans) for child in children]
        }


class TraceContext:
    """Context manager for tracing"""

    def __init__(self, tracer: Tracer, operation_name: str, kind: SpanKind = SpanKind.INTERNAL):
        self.tracer = tracer
        self.operation_name = operation_name
        self.kind = kind
        self.span: Optional[Span] = None

    def __enter__(self) -> Span:
        """Enter context"""
        self.span = self.tracer.start_span(
            self.operation_name,
            kind=self.kind
        )
        return self.span

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context"""
        if self.span:
            if exc_type:
                self.span.set_status(SpanStatus.ERROR)
                self.span.add_event(
                    "exception",
                    {
                        "exception.type": type(exc_val).__name__,
                        "exception.message": str(exc_val)
                    }
                )
            else:
                self.span.set_status(SpanStatus.OK)

            self.span.end()


# Global tracer instance
_global_tracer = Tracer()


def get_tracer() -> Tracer:
    """Get global tracer"""
    return _global_tracer


class SpanDecorator:
    """Decorator for tracing functions"""

    def __init__(self, operation_name: Optional[str] = None, kind: SpanKind = SpanKind.INTERNAL):
        self.operation_name = operation_name
        self.kind = kind

    def __call__(self, func):
        """Decorate function"""
        async def async_wrapper(*args, **kwargs):
            operation_name = self.operation_name or func.__name__
            tracer = get_tracer()

            with TraceContext(tracer, operation_name, self.kind) as span:
                try:
                    result = await func(*args, **kwargs)
                    return result
                except Exception as e:
                    span.set_status(SpanStatus.ERROR)
                    raise

        def sync_wrapper(*args, **kwargs):
            operation_name = self.operation_name or func.__name__
            tracer = get_tracer()

            with TraceContext(tracer, operation_name, self.kind) as span:
                try:
                    result = func(*args, **kwargs)
                    return result
                except Exception as e:
                    span.set_status(SpanStatus.ERROR)
                    raise

        # Return appropriate wrapper
        if hasattr(func, "__await__"):
            return async_wrapper
        else:
            return sync_wrapper
