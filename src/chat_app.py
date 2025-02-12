from flask import Flask, render_template, request, jsonify
from services.claims_service import claims_service

app = Flask(__name__)


def get_chat_response(input):
    return "Hi!"


@app.route("/")
def homepage():
    # Replace this with actual data retrieval logic
    claims_data = ["Claim 1", "Claim 2", "Claim 3"]
    return render_template("homepage.html", claims=claims_data)


@app.route("/chat_get", methods=["GET", "POST"])
def chat_get():
    msg = request.form["msg"]
    return get_chat_response(msg)


@app.route("/claims", methods=["GET"])
def get_Claims():
    claims = claims_service.get_all_claims()
    return claims


@app.route("/claims/{claim_id}", methods=["GET"])
def get_Claim(claim_id):
    claim = claims_service.get_claim_by_id(claim_id)
    return claim


@app.route("/claims/{claim_id}/conversations", methods=["GET"])
def get_Conversations(claim_id):
    # todo: retrieve conversations with claim_id from cosmos db
    return ""


@app.route("/claims/{claim_id}/conversations/{conversation_id}", methods=["GET"])
def get_Claims(claim_id, conversation_id):
    # todo: retrieve conversation with claim_id and conversation_id from cosmos db
    return ""


@app.route("/claims/{claim_id}/conversations/{conversation_id}", methods=["POST"])
def get_Claims(claim_id, conversation_id):
    # todo: perform chat here
    return ""


@app.route("/claims/{claim_id}/conversations/{conversation_id}", methods=["DELETE"])
def get_Claims(claim_id, conversation_id):
    # todo: delete conversation with claim_id and conversation_id from cosmos db
    return ""


if __name__ == "__main__":
    app.run(debug=False)
