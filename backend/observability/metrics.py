"""
Prometheus metrics setup.
"""
from prometheus_client import Counter, Histogram, Gauge, start_http_server
from typing import Optional

from app.core.config import settings

# HTTP metrics
http_requests_total = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status_code"],
)

http_request_duration = Histogram(
    "http_request_duration_seconds",
    "HTTP request duration in seconds",
    ["method", "endpoint"],
)

# Video processing metrics
video_processing_jobs_total = Counter(
    "video_processing_jobs_total",
    "Total video processing jobs",
    ["status"],
)

video_processing_duration = Histogram(
    "video_processing_duration_seconds",
    "Video processing duration in seconds",
    ["camera_id"],
)

events_detected_total = Counter(
    "events_detected_total",
    "Total events detected",
    ["event_type", "severity"],
)

# GPU metrics
gpu_utilization = Gauge(
    "gpu_utilization_percent",
    "GPU utilization percentage",
    ["gpu_id"],
)

gpu_memory_used = Gauge(
    "gpu_memory_used_bytes",
    "GPU memory used in bytes",
    ["gpu_id"],
)

# Queue metrics
queue_size = Gauge(
    "queue_size",
    "Current queue size",
    ["queue_name"],
)

# Database metrics
db_connections_active = Gauge(
    "db_connections_active",
    "Active database connections",
)

db_query_duration = Histogram(
    "db_query_duration_seconds",
    "Database query duration in seconds",
    ["query_type"],
)


def start_metrics_server(port: Optional[int] = None) -> None:
    """
    Start Prometheus metrics HTTP server.
    
    Args:
        port: Port to listen on (defaults to settings.PROMETHEUS_PORT)
    """
    if port is None:
        port = settings.PROMETHEUS_PORT
    start_http_server(port)
    get_logger(__name__).info("Prometheus metrics server started", port=port)


def get_logger(name: str):
    """Import logger function."""
    from observability.logging import get_logger
    return get_logger(name)

