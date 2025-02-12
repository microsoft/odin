from flask import Flask, render_template, request, jsonify

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