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
from sqlalchemy.ext.asyncio.engine import AsyncEngine


def setup_telemetry(
    app: FastAPI,
    *,
    sentry_dsn: str | None,
    sentry_traces_sample_rate: float,
    environment: str,
    otlp_endpoint: str,
    product_name: str,
    async_engine: AsyncEngine,
) -> None:
    """Инициализация Sentry и OpenTelemetry."""

    if sentry_dsn:
        sentry_sdk.init(
            dsn=sentry_dsn,
            environment=environment,
            traces_sample_rate=sentry_traces_sample_rate,
            send_default_pii=False,
            instrumenter="otel",
        )

    resource = Resource.create({"service.name": f"auth-service-{product_name}"})
    provider = TracerProvider(resource=resource)

    otlp_exporter = OTLPSpanExporter(endpoint=otlp_endpoint, insecure=True)
    provider.add_span_processor(BatchSpanProcessor(otlp_exporter))

    if sentry_dsn:
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
