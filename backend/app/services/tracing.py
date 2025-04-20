import logging
import os

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.logging import LoggingInstrumentor
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.trace import get_current_span


class SafeFormatter(logging.Formatter):
    def format(self, record):
        span = get_current_span()
        ctx = span.get_span_context() if span else None

        record.otelTraceID = format(ctx.trace_id, "032x") if ctx and ctx.trace_id else "0"
        record.otelSpanID = format(ctx.span_id, "016x") if ctx and ctx.span_id else "0"
        return super().format(record)


handler = logging.StreamHandler()
handler.setFormatter(
    SafeFormatter(fmt="%(asctime)s [%(levelname)s] [trace_id=%(otelTraceID)s span_id=%(otelSpanID)s] %(message)s")
)

logging.getLogger().handlers.clear()
logging.getLogger().addHandler(handler)
logging.getLogger().setLevel(logging.INFO)
logger = logging.getLogger("tracing_test")


def setup_tracing(app):
    # HTTP Exporter to Grafana Alloy (Tempo)
    OTLP_ENDPOINT = os.getenv("OTLP_ENDPOINT")
    if not OTLP_ENDPOINT:
        print("Missing OTLP_ENDPOINT environment variable")
        return
    provider = TracerProvider(resource=Resource.create({SERVICE_NAME: "backend"}))
    trace.set_tracer_provider(provider)

    exporter = OTLPSpanExporter(endpoint=OTLP_ENDPOINT, insecure=True)
    span_processor = BatchSpanProcessor(exporter)
    provider.add_span_processor(span_processor)

    # Automatically instrument FastAPI routes
    FastAPIInstrumentor.instrument_app(app, tracer_provider=provider)
    LoggingInstrumentor().instrument(set_logging_format=True)
    logger.info("✅ Tracing and logging initialized successfully")
