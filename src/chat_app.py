from flask import Flask, render_template, request, jsonify
from config import AppConfig
from setup_logging import set_up_logging, set_up_metrics, set_up_tracing

config = AppConfig()

# setup SK logging, metrics, and tracing
set_up_logging(config=config)
set_up_tracing(config=config)
set_up_metrics(config=config)

# Configure OpenTelemetry to use Azure Monitor, this is the auto instrumentation
from azure.monitor.opentelemetry import configure_azure_monitor
configure_azure_monitor(connnection_string=config.app_insights_connstr)

app = Flask(__name__)

def get_chat_response(input):
    return "Hi!"

@app.route('/')
def homepage():
    # Replace this with actual data retrieval logic
    claims_data = ["Claim 1", "Claim 2", "Claim 3"]
    return render_template("homepage.html", claims=claims_data)

@app.route("/chat_get", methods=["GET", "POST"])
def chat_get():
    msg = request.form["msg"]
    return get_chat_response(msg)

if __name__ == '__main__': 
    app.run(debug=False) 