from flask import Flask, request
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.otlp.proto.grpc.logs_exporter import OTLPLogExporter
from opentelemetry.exporter.azure.monitor import AzureMonitorTraceExporter, AzureMonitorLogExporter
import logging
import os

# Set up environment variables for Azure Application Insights
APP_INSIGHTS_CONNECTION_STRING = "YOUR_CONNECTION_STRING_HERE"

# Set up OpenTelemetry tracing
trace_provider = TracerProvider()
trace_exporter = AzureMonitorTraceExporter.from_connection_string(APP_INSIGHTS_CONNECTION_STRING)
trace_provider.add_span_processor(BatchSpanProcessor(trace_exporter))
from opentelemetry.trace import set_tracer_provider
set_tracer_provider(trace_provider)
tracer = trace_provider.get_tracer(__name__)

# Set up OpenTelemetry logging
log_provider = LoggerProvider()
log_exporter = AzureMonitorLogExporter.from_connection_string(APP_INSIGHTS_CONNECTION_STRING)
log_provider.add_log_record_processor(BatchLogRecordProcessor(log_exporter))
logging.basicConfig(level=logging.INFO)
handler = LoggingHandler(level=logging.INFO, logger_provider=log_provider)
logging.getLogger().addHandler(handler)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)
FlaskInstrumentor().instrument_app(app)

@app.route("/")
def home():
    with tracer.start_as_current_span("home-request") as span:
        span.set_attribute("http.method", request.method)
        span.set_attribute("http.url", request.url)
        logger.info("Home endpoint was hit", extra={"custom_attribute": "example_value"})
    return "Hello, OpenTelemetry with Flask and App Insights!"

@app.route("/error")
def error():
    with tracer.start_as_current_span("error-request"):
        logger.error("An error occurred", extra={"error": "example error"})
        return "This is an error endpoint", 500

if __name__ == "__main__":
    app.run(debug=True)