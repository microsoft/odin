from flask import Flask, json, make_response, render_template, request, jsonify
from cai_chat.cai_chat import run_agent
from nonessential.rand_chat import get_random_response
from nonessential.local_file_for_chat_history import local_file_for_chat_history
from nonessential.azure_blob_for_chat_history import azure_blob_for_chat_history
from models.claim import Claim
from models.conversation import Conversation
from services.claims_service import claims_service
import json

app = Flask(__name__)


@app.route("/health")
def health():
    return "OK"


@app.route("/")
def homepage():
    # Replace this with actual data retrieval logic
    claims = claims_service.get_all()
    return render_template("homepage.html", claims=claims)


@app.route("/claims", methods=["GET"])
def get_claims():
    claims = claims_service.get_all()
    dicts = [claim.to_dict() for claim in claims]
    return json.dumps(dicts)


@app.route("/claims/<claim_id>", methods=["GET"])
def get_claim(claim_id):
    if isinstance(claim_id, str):
        try:
            claim_id = int(claim_id)
        except ValueError:
            return json.dumps({"error": "Invalid claim ID"}), 400
    claim = claims_service.get_by_id(claim_id)
    if not claim:
        return json.dumps({"error": "Claim not found"}), 404
    return json.dumps(claim.to_dict())


@app.route("/claims", methods=["POST"])
def upsert_claim():
    claim_data = request.get_json()
    try:
        claim = Claim(**claim_data)
    except (TypeError, ValueError) as e:
        return json.dumps({"error": str(e)}), 400
    claims_service.upsert(claim)
    return make_response("Accepted", 202)


@app.route("/claims/<claim_id>", methods=["DELETE"])
def delete_claim(claim_id: int):
    if isinstance(claim_id, str):
        try:
            claim_id = int(claim_id)
        except ValueError:
            return json.dumps({"error": "Invalid claim ID"}), 400
    claims_service.delete(claim_id)
    return make_response("Accepted", 202)


@app.route("/claims/<claim_id>/conversations", methods=["GET"])
def get_conversations(claim_id: int):
    return (
        "todo: return conversations with claim_id from cosmos db. claim_id = "
        + claim_id
    )


@app.route("/claims/<claim_id>/conversations/<conversation_id>", methods=["GET"])
def get_conversation(claim_id: int, conversation_id: int):
    return (
        "todo: retrieve conversation with claim_id and conversation_id from cosmos db. claim_id = "
        + claim_id
        + ", conversation_id = "
        + conversation_id
    )


@app.route(
    "/claims/<claim_id>/conversations",
    defaults={"conversation_id": None},
    methods=["POST"],
)
@app.route("/claims/<claim_id>/conversations/<conversation_id>", methods=["POST"])
def converse(claim_id: int, conversation_id: int):

    request_json = request.get_json()
    print("request_json: ", request_json)
    conversation = Conversation(**request_json)
    print("conversation: ", conversation)

    use_cosmos_for_chat_history = False # Focus of project
    use_azure_blob_for_chat_history = False # Added for debugging & development purposes
    use_local_file_for_chat_history = True # Added for debugging & development purposes

    if use_cosmos_for_chat_history:
        chat_history = conversation.messages # TODO
    elif use_azure_blob_for_chat_history: ### USING AZURE BLOB FOR CHAT HISTORY
        chat_history = azure_blob_for_chat_history(request_json, conversation_id, recall_history_only=True)
    elif use_local_file_for_chat_history:
        chat_history = local_file_for_chat_history(request_json, conversation_id, recall_history_only=True)

    # if we have an agent, set to True, otherwise set to False for development purposes
    agent_available = True
    if agent_available:
        conv_result = run_agent(conversation.messages[-1]["content"], chat_history)
    else:
        conv_result = get_random_response(conversation.messages[-1]["content"], chat_history)
    print("conv_result: ", conv_result)

    

    if use_cosmos_for_chat_history:

        # if conversation does not exist, initialize one
        #
        # if one does exist, retrieve the history, append the message to it
        #
        # maybe need to change up the model a bit
        #
        # we probably only want to be passing the last message back and forth
        # and just let fetching of full conversation history be the GET endpoints concern
        #
        pass

    elif use_azure_blob_for_chat_history: ### USING AZURE BLOB FOR CHAT HISTORY
        _ = azure_blob_for_chat_history(request_json, conversation_id, recall_history_only=False, conv_result=conv_result)
        
    elif use_local_file_for_chat_history:
        _ = local_file_for_chat_history(request_json, conversation_id, recall_history_only=False, conv_result=conv_result)

    return jsonify(conv_result["generation"])


@app.route("/claims/<claim_id>/conversations/<conversation_id>", methods=["DELETE"])
def delete_conversation(claim_id: int, conversation_id: int):
    return (
        "# todo: delete conversation with claim_id and conversation_id from cosmos db. claim_id = "
        + claim_id
        + ", conversation_id = "
        + conversation_id
    )


if __name__ == "__main__":
    app.run(debug=False)
