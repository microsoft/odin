from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

def get_chat_response(input):
    return "Hi!"

@app.route('/')
def homepage():
    return render_template("homepage.html")

@app.route("/chat_get", methods=["GET", "POST"])
def chat_get():
    msg = request.form["msg"]
    return get_chat_response(msg)

if __name__ == '__main__': 
    app.run(debug=False) 