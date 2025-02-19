from setup_logging import setup_azure_monitor

setup_azure_monitor()

from config import config
from azure.monitor.opentelemetry import configure_azure_monitor
configure_azure_monitor(connection_string=config.app_insights_connstr)

from datetime import datetime
import uuid
from flask import Flask, json, make_response, render_template, request, jsonify
from auth.utils import get_authenticated_user_details
from cai_chat.cai_chat import run_agent
from models.claim import Claim
from models.conversation import Conversation
#from services.conversation_service import conversation_service
from services.claims_service import claims_service
# you can create an auth service to to get this value
# or retrieve from user claims on jwt
# for now we are using a hardcoded value
user_group_id = "claims_managers"

app = Flask(__name__)


@app.route("/health")
def health():
    return "OK"


@app.route("/")
def homepage():
    user = get_authenticated_user_details(request.headers)
    # Replace this with actual data retrieval logic
    claims = claims_service.get_all(user["user_principal_id"])
    return render_template("homepage.html", claims=claims)


@app.route("/claims", methods=["GET"])
def get_claims():
    user = get_authenticated_user_details(request.headers)

    claims = claims_service.get_all(user["user_principal_id"])
    dicts = [claim.to_dict() for claim in claims]
    return json.dumps(dicts)


@app.route("/claims/<claim_id>", methods=["GET"])
def get_claim(claim_id: str):
    user = get_authenticated_user_details(request.headers)

    claim = claims_service.get_by_id(user["user_principal_id"], claim_id)
    if not claim:
        return json.dumps({"error": "Claim not found"}), 404

    return json.dumps(claim.to_dict())


@app.route("/claims", methods=["POST"])
def upsert_claim():
    user = get_authenticated_user_details(request.headers)

    claim_data = request.get_json()
    try:
        claim = Claim(**claim_data, user_id=user["user_principal_id"])
    except (TypeError, ValueError) as e:
        return json.dumps({"error": str(e)}), 400

    claims_service.upsert(claim)

    return make_response("Accepted", 202)


@app.route("/claims/<claim_id>", methods=["DELETE"])
def delete_claim(claim_id: str):
    user = get_authenticated_user_details(request.headers)

    claims_service.delete(user["user_principal_id"], claim_id)

    return make_response("Accepted", 202)


@app.route("/claims/<claim_id>/conversations", methods=["GET"])
def get_conversations(claim_id: str):
    user = get_authenticated_user_details(request.headers)

    conversations = conversation_service.get_conversations(
        user["user_principal_id"], claim_id
    )

    return json.dumps([conversation.to_dict() for conversation in conversations])


@app.route("/claims/<claim_id>/conversations/<conversation_id>", methods=["GET"])
def get_conversation(claim_id: str, conversation_id: str):
    user = get_authenticated_user_details(request.headers)

    claim = claims_service.get_by_id(user["user_principal_id"], claim_id)
    if not claim:
        return json.dumps({"error": "Claim not found"}), 404

    conversation = conversation_service.get_conversation(
        user["user_principal_id"], claim_id, conversation_id
    )

    if not conversation:
        return json.dumps({"error": "Conversation not found"}), 404

    return json.dumps(conversation.to_dict())


@app.route(
    "/claims/<claim_id>/conversations",
    defaults={"conversation_id": None},
    methods=["POST"],
)
@app.route("/claims/<claim_id>/conversations/<conversation_id>", methods=["POST"])
def converse(claim_id: str, conversation_id: str):
    user = get_authenticated_user_details(request.headers)

    claim = claims_service.get_by_id(user["user_principal_id"], claim_id)
    if not claim:
        return json.dumps({"error": "Claim not found"}), 404

    request_json = request.get_json()

    if "id" not in request_json:
        if conversation_id is not None and conversation_id != "":
            request_json["id"] = conversation_id
        else:
            request_json["id"] = str(uuid.uuid4())
    elif request_json["id"] != conversation_id:
        return json.dumps({"error": "Mismatched conversation ID"}), 400

    conversation = Conversation(
        **request_json, user_id=user["user_principal_id"], user_group_id=user_group_id
    )

    if (
        conversation.id != conversation_id and conversation_id is not None
    ) or conversation.claim_id != claim_id:
        return json.dumps({"error": "Mismatched conversation ID or claim ID"}), 400

    conversation_service.upsert_conversation(conversation)

    conv_result = run_agent(
        conversation.messages[-1]["content"],
        claimnumber=claim_id,
        chat_history=conversation.messages,
    )

    conversation.messages.append(
        {
            "content": conv_result["generation"],
            "date": datetime.now().isoformat(),
            "role": "assistant",
        }
    )

    conversation_service.upsert_conversation(conversation)

    return jsonify(conversation.to_dict())


@app.route("/claims/<claim_id>/conversations/<conversation_id>", methods=["DELETE"])
def delete_conversation(claim_id: str, conversation_id: str):
    user = get_authenticated_user_details(request.headers)

    claim = claims_service.get_by_id(user["user_principal_id"], claim_id)
    if not claim:
        return json.dumps({"error": "Claim not found"}), 404

    conversation_service.delete_conversation(
        user["user_principal_id"], claim_id, conversation_id
    )

    return make_response("Accepted", 202)


if __name__ == "__main__":
    app.run(debug=False)