# src/core/telemetry.py
import sentry_sdk
from fastapi import FastAPI
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.redis import RedisInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from sentry_sdk.integrations.opentelemetry import SentrySpanProcessor

from src.core.settings import config
from src.db import async_engine


def setup_telemetry(app: FastAPI) -> None:
    """Инициализация Sentry и OpenTelemetry."""

    if config.SENTRY_DSN:
        sentry_sdk.init(
            dsn=config.SENTRY_DSN,
            environment=config.ENVIRONMENT,
            traces_sample_rate=config.SENTRY_TRACES_SAMPLE_RATE,
            send_default_pii=False,
            instrumenter="otel",
        )

    resource = Resource.create({"service.name": f"auth-service-{config.PRODUCT_NAME}"})
    provider = TracerProvider(resource=resource)

    otlp_exporter = OTLPSpanExporter(endpoint=config.OTLP_ENDPOINT, insecure=True)
    provider.add_span_processor(BatchSpanProcessor(otlp_exporter))

    if config.SENTRY_DSN:
        provider.add_span_processor(SentrySpanProcessor())

    trace.set_tracer_provider(provider)

    from opentelemetry.propagate import set_global_textmap
    from opentelemetry.trace.propagation.tracecontext import (
        TraceContextTextMapPropagator,
    )

    set_global_textmap(TraceContextTextMapPropagator())

    SQLAlchemyInstrumentor().instrument(
        engine=async_engine.sync_engine, enable_commenter=True, commenter_options={}
    )

    RedisInstrumentor().instrument()

    FastAPIInstrumentor.instrument_app(
        app,
        excluded_urls="docs,openapi.json,metrics,health,ready",
    )
