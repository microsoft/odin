from flask import Flask, request, jsonify
from flask_restful import Resource, Api
from cai_chat.cai_chat import run_agent

app = Flask(__name__)
api = Api(app)

class OdinAgent(Resource):
    def post(self):
        request_json = request.get_json()  # Parse the JSON data from the request
        conv_result = run_agent(
            request_json['messages'][-1]["content"],
            claimnumber=request_json['claim_id'],
            chat_history=request_json['messages'],
        )
        return conv_result["generation"], 200

api.add_resource(OdinAgent, '/odin')

if __name__ == '__main__':
    app.run(debug=True, port=5444)
