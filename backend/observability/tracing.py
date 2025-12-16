"""
OpenTelemetry tracing setup.
"""
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor

from app.core.config import settings


def setup_tracing(app=None) -> None:
    """
    Configure OpenTelemetry tracing.
    
    Args:
        app: FastAPI application instance (optional)
    """
    # Create resource
    resource = Resource.create({
        "service.name": settings.APP_NAME,
        "service.version": settings.APP_VERSION,
    })
    
    # Create tracer provider
    provider = TracerProvider(resource=resource)
    
    # Add OTLP exporter
    if hasattr(settings, "OTEL_EXPORTER_OTLP_ENDPOINT"):
        otlp_exporter = OTLPSpanExporter(
            endpoint=settings.OTEL_EXPORTER_OTLP_ENDPOINT,
        )
        provider.add_span_processor(BatchSpanProcessor(otlp_exporter))
    
    # Set global tracer provider
    trace.set_tracer_provider(provider)
    
    # Instrument FastAPI if app is provided
    if app is not None:
        FastAPIInstrumentor.instrument_app(app)
    
    # Instrument other libraries
    RequestsInstrumentor().instrument()
    SQLAlchemyInstrumentor().instrument()


def get_tracer(name: str):
    """
    Get a tracer instance.
    
    Args:
        name: Tracer name (typically __name__)
        
    Returns:
        Tracer instance
    """
    return trace.get_tracer(name)

