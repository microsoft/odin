import logging
from config import config
from azure.monitor.opentelemetry.exporter import (
    AzureMonitorLogExporter,
    AzureMonitorMetricExporter,
    AzureMonitorTraceExporter,
)
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry._logs import set_logger_provider
from opentelemetry.metrics import set_meter_provider
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.semconv.resource import ResourceAttributes
from opentelemetry.trace import set_tracer_provider
from openinference.instrumentation.langchain import LangChainInstrumentor


# Create a resource to represent the service/sample
resource = Resource.create(
    {ResourceAttributes.SERVICE_NAME: "telemetry-application-insights-quickstart"}
)


def filter_out_azure_monitor(record: logging.LogRecord) -> bool:
    return not (
        record.name.startswith("azure.monitor.")
        or record.name.startswith("azure.core.pipeline.policies.http_logging_policy")
    )


def set_up_logging():
    exporter = AzureMonitorLogExporter(connection_string=config.app_insights_connstr)

    # Create and set a global logger provider for the application.
    logger_provider = LoggerProvider(resource=resource)
    # Log processors are initialized with an exporter which is responsible
    # for sending the telemetry data to a particular backend.
    logger_provider.add_log_record_processor(BatchLogRecordProcessor(exporter))
    # Sets the global default logger provider
    set_logger_provider(logger_provider)

    # Events from all child loggers will be processed by this handler.
    logger = logging.getLogger()

    # Create a logging handler to write logging records, in OTLP format, to the exporter.
    handler = LoggingHandler()
    handler.addFilter(filter_out_azure_monitor)
    logger.addHandler(handler)

    # Add a stream handler to the logger to print the logs to the console.
    stream_handler = logging.StreamHandler()
    stream_handler.addFilter(filter_out_azure_monitor)
    logger.addHandler(stream_handler)

    logger.setLevel(logging.INFO)
    return logger_provider


def set_up_tracing():
    exporter = AzureMonitorTraceExporter(connection_string=config.app_insights_connstr)

    # Initialize a trace provider for the application. This is a factory for creating tracers.
    tracer_provider = TracerProvider(resource=resource)

    # Span processors are initialized with an exporter which is responsible
    # for sending the telemetry data to a particular backend.
    tracer_provider.add_span_processor(BatchSpanProcessor(exporter))

    # Sets the global default tracer provider
    set_tracer_provider(tracer_provider)
    return tracer_provider


def set_up_metrics():
    exporter = AzureMonitorMetricExporter(connection_string=config.app_insights_connstr)

    # Initialize a metric provider for the application. This is a factory for creating meters.
    meter_provider = MeterProvider(
        metric_readers=[
            PeriodicExportingMetricReader(exporter, export_interval_millis=5000)
        ],
        resource=resource,
    )

    # Sets the global default meter provider
    set_meter_provider(meter_provider)
    return meter_provider


def setup_azure_monitor():
    set_up_logging()
    tracer_provider = set_up_tracing()
    set_up_metrics()
    FlaskInstrumentor().instrument(tracer_provider=tracer_provider)
    LangChainInstrumentor().instrument(tracer_provider=tracer_provider)


__all__ = [setup_azure_monitor]
