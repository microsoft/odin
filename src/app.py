from datetime import datetime
from flask import Flask, json, make_response, render_template, request, jsonify
from cai_chat.cai_chat import run_agent
from models.claim import Claim
from models.conversation import Conversation
# from services.conversation_service import conversation_service
from services.claims_service import claims_service
from nonessential.rand_chat import get_random_response
from nonessential.local_file_for_chat_history import local_file_for_chat_history
from nonessential.azure_blob_for_chat_history import azure_blob_for_chat_history
from config import config

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
def get_claim(claim_id: str):
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
def delete_claim(claim_id: str):
    claims_service.delete(claim_id)
    return make_response("Accepted", 202)


@app.route("/claims/<claim_id>/conversations", methods=["GET"])
def get_conversations(claim_id: str):
    conversations = conversation_service.get_conversations(claim_id)

    return json.dumps([conversation.to_dict() for conversation in conversations])


@app.route("/claims/<claim_id>/conversations/<conversation_id>", methods=["GET"])
def get_conversation(claim_id: str, conversation_id: str):
    conversation = conversation_service.get_conversation(claim_id, conversation_id)

    return json.dumps(conversation.to_dict())


@app.route(
    "/claims/<claim_id>/conversations",
    defaults={"conversation_id": None},
    methods=["POST"],
)
@app.route("/claims/<claim_id>/conversations/<conversation_id>", methods=["POST"])
def converse(claim_id: str, conversation_id: str):
    request_json = request.get_json()
    conversation = Conversation(**request_json)

    if (
        (conversation.id != conversation_id and conversation_id is not None)
        or conversation.claim_id != claim_id
    ):
        return json.dumps({"error": "Mismatched conversation ID or claim ID"}), 400
    

    def get_ai_response(conversation, chat_history):
        # if we have an agent, set to True, otherwise set to False for development purposes
        agent_available = True
        if agent_available:
            conv_result = run_agent(conversation.messages[-1]["content"], chat_history)
        else:
            conv_result = get_random_response(conversation.messages[-1]["content"], chat_history)
        return conv_result


    if config.use_cosmos_for_chat_history:

        # if conversation does not exist, initialize one
        #
        # if one does exist, retrieve the history, append the message to it
        chat_history = conversation.messages # TODO
        # maybe need to change up the model a bit
        #
        # we probably only want to be passing the last message back and forth
        # and just let fetching of full conversation history be the GET endpoints concern
        #


        conv_result = run_agent(conversation.messages[-1]["content"], claimnumber=claim_id, chat_history=conversation.messages)

        # faking chat for now
        conversation.messages.append(conv_result)

        conversation_service.upsert_conversation(conversation)

        return jsonify(conversation.to_dict())


    elif config.use_azure_blob_for_chat_history: ### USING AZURE BLOB FOR CHAT HISTORY
        # get chat history
        chat_history = azure_blob_for_chat_history(request_json, conversation_id, recall_history_only=True)
        # get AI response
        get_ai_response(conversation, chat_history)
        # update chat history
        _ = azure_blob_for_chat_history(request_json, conversation_id, recall_history_only=False, conv_result=conv_result)
        # return result
        return jsonify(conv_result["generation"])
    
    elif config.use_local_file_for_chat_history:
        # get chat history
        chat_history = local_file_for_chat_history(request_json, conversation_id, recall_history_only=True)
        # get AI response
        get_ai_response(conversation, chat_history)
        # update chat history
        _ = local_file_for_chat_history(request_json, conversation_id, recall_history_only=False, conv_result=conv_result)
        # return result
        return jsonify(conv_result["generation"])
    
    else:
        return jsonify("I'm sorry, I'm curring experiencing technical issues. Please try again later.")

    


@app.route("/claims/<claim_id>/conversations/<conversation_id>", methods=["DELETE"])
def delete_conversation(claim_id: str, conversation_id: str):
    conversation_service.delete_conversation(claim_id, conversation_id)

    return make_response("Accepted", 202)


if __name__ == "__main__":
    app.run(debug=False)
