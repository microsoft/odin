from config import config

from setup_logging import setup_azure_monitor

setup_azure_monitor()

from datetime import datetime
import uuid
from flask import Flask, json, make_response, render_template, request, jsonify
from auth.utils import get_authenticated_user_details
from cai_chat.cai_chat import run_agent
from models.claim import Claim
from models.conversation import Conversation
from services.conversation_service import conversation_service
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

    connection_string = config.app_insights_connstr
    # Replace this with actual data retrieval logic
    claims = claims_service.get_all(user["user_principal_id"])
    # When we hit the homepage, the dropdown will auto select the first claim, so that's the claim we'll pass here
    conversations = conversation_service.get_conversations(
        user["user_principal_id"], claims[0].claim_id
    )
    return render_template(
        "homepage.html",
        claims=claims,
        conversations=conversations,
        app_insights_connection_string=connection_string,
    )


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

    if "id" not in request_json:  # it's either a new conversation or a bad request
        if (
            conversation_id is not None and conversation_id != ""
        ):  # it's an existing conversation but the id is missing
            return json.dumps({"error": "Route and request body id mismatch."}), 400
        else:
            request_json["id"] = str(uuid.uuid4())
            conversation = Conversation(
                **request_json,
                user_id=user["user_principal_id"],
                user_group_id=user_group_id
            )
    elif request_json["id"] != conversation_id and (
        conversation_id is not None and conversation_id != ""
    ):  # it's an existing conversation but the id doesn't match
        return json.dumps({"error": "Route and request body id mismatch."}), 400
    else:  # it's an existing conversation
        conversation = Conversation(
            **request_json,
            user_id=user["user_principal_id"],
            user_group_id=user_group_id
        )
    ### since we landed on sending and receiving the full conversation, we can comment out the below code for now
    ### in favor of the else above, you may consider using the below if you want to send and receive the
    ### last message only which can improve latency by reducing payload size
    # else:  # it's an existing conversation
    #     # grab convo with all it's history
    #     conversation = conversation_service.get_conversation(
    #         user["user_principal_id"], request_json["claim_id"], request_json["id"]
    #     )
    #     conversation.messages.append(
    #         request_json["messages"][0]
    #     )  # append the new question to messages

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
