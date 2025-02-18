# Logic from Gemini

import logging
import os

from flask import Flask
from opentelemetry import trace
from opentelemetry.exporter.applicationinsights import ApplicationInsightsLogExporter
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.logging import LoggingInstrumentor
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator


# Replace with your Application Insights connection string
APPLICATION_INSIGHTS_CONNECTION_STRING = os.environ.get("APPLICATION_INSIGHTS_CONNECTION_STRING") or "YOUR_CONNECTION_STRING"  #  Use environment variables for production!

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)  # Set your desired logging level

# Initialize OpenTelemetry
resource = Resource.create({"service.name": "my-flask-app"}) # Important: Provide a service name

# Logging setup
logger_provider = LoggerProvider(resource=resource)
LoggingInstrumentor().instrument(logger_provider=logger_provider)  # Instrument standard logging

# Application Insights Log Exporter
if APPLICATION_INSIGHTS_CONNECTION_STRING:
    log_exporter = ApplicationInsightsLogExporter(
        connection_string=APPLICATION_INSIGHTS_CONNECTION_STRING
    )
    logger_provider.add_log_record_processor(log_exporter)
else:
    logging.warning("Application Insights connection string not found.  Logs will not be exported.")



# Tracing setup (for correlating logs and traces)
tracer_provider = TracerProvider(resource=resource)
trace.set_tracer_provider(tracer_provider)
tracer = trace.get_tracer(__name__)
trace_exporter = ApplicationInsightsLogExporter(
    connection_string=APPLICATION_INSIGHTS_CONNECTION_STRING
)  # Reuse the same exporter for traces too.
tracer_provider.add_span_processor(SimpleSpanProcessor(trace_exporter))

# Inject trace context for correlation
trace_context_propagator = TraceContextTextMapPropagator()
trace.set_text_map_propagator(trace_context_propagator)


# Instrument Flask
FlaskInstrumentor().instrument_app(app)


@app.route("/")
def hello():
    # Example structured logging
    app.logger.info({"message": "Hello, world!", "user_id": 123, "details": {"nested_info": "some value"}})  # Structured logging is highly recommended!

    # Example standard logging
    app.logger.info("This is a standard log message.")

    # Example with tracing (to demonstrate correlation)
    with tracer.start_as_current_span("hello-span"):
        app.logger.info("Log message within a trace.")
        # Add more context to the span if needed.
        span = trace.get_current_span()
        span.set_attribute("my_custom_attribute", "some_value")

    return "Hello, World!"


if __name__ == "__main__":
    app.run(debug=True)  # Set debug=False in production