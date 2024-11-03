from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from C_L_E_A_N import generate_response  # Import the chatbot logic

# Initialize Flask app
app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return "C.L.E.A.N Chatbot is running!"

    # return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.json.get('message')  # Gets the user messages from the JSON request
    response = generate_response(user_input)  # This Calls the chatbot logic.
    return jsonify({'response': response})

if __name__ == "__main__":
    app.run(port=8080,debug=True)
