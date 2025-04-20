# app/tracing.py

import os

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor


def setup_tracing(app):
    # HTTP Exporter to Grafana Alloy (Tempo)
    OTLP_ENDPOINT = os.getenv("OTLP_ENDPOINT")
    if not OTLP_ENDPOINT:
        print("Missing OTLP_ENDPOINT environment variable")
        return
    provider = TracerProvider(resource=Resource.create({SERVICE_NAME: "backend"}))
    trace.set_tracer_provider(provider)

    exporter = OTLPSpanExporter(endpoint=OTLP_ENDPOINT)

    span_processor = BatchSpanProcessor(exporter)
    provider.add_span_processor(span_processor)

    # Automatically instrument FastAPI routes
    FastAPIInstrumentor.instrument_app(app, tracer_provider=provider)
