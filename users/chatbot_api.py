
from flask import Flask, request, jsonify
from chatbot_nlp import chatbot, save_training_data, load_training_data

app = Flask(__name__)

@app.route('/chatbot', methods=['POST'])
def chatbot_response():
    user_message = request.json.get('message')
    response = chatbot.respond(user_message)

    # Save user interactions for future learning
    training_data = load_training_data()
    training_data.append([user_message, [response]])
    save_training_data(training_data)

    return jsonify({"response": response})

if __name__ == '__main__':
    app.run(port=5005, debug=True)
    
    
from chatbot_nlp import get_chatbot_response

@app.route('/chatbot', methods=['POST'])
def chatbot_response():
    user_message = request.json.get('message')
    response = get_chatbot_response(user_message)

    # Save user interactions for future learning
    training_data = load_training_data()
    training_data.append([user_message, [response]])
    save_training_data(training_data)

    return jsonify({"response": response})