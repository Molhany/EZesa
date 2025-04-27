import nltk
from nltk.chat.util import Chat, reflections
import json

# Load training data
def load_training_data():
    try:
        with open('training_data.json', 'r') as file:
            data = json.load(file)
        return data
    except FileNotFoundError:
        return []

# Save training data
def save_training_data(data):
    with open('training_data.json', 'w') as file:
        json.dump(data, file, indent=4)

training_data = load_training_data()

# Update pairs with new training data
pairs = training_data + [
    [
        r"(hi|hello|hey)",
        ["Hello! How can I help you today?",]
    ],
    [
        r"what is your name?",
        ["I am EZesa Chatbot, your virtual assistant.",]
    ],
    [
        r"how do I (purchase|buy) energy?",
        ["You can purchase energy by navigating to the 'Energy' section and clicking on 'Purchase Energy'.",]
    ],
    [
        r"how do I view my bills?",
        ["You can view your bills by navigating to the 'Bills' section in the sidebar.",]
    ],
    [
        r"(.*) support",
        ["You can contact our support team using the form on this page or by submitting a support ticket.",]
    ],
    [
        r"thanks|thank you",
        ["You're welcome! If you have any other questions, feel free to ask.",]
    ]
]

chatbot = Chat(pairs, reflections)



from .weather_api import get_weather

pairs = training_data + [
    ...
    [
        r"what is the weather in (.*)?",
        ["Let me check the weather in %1.",]
    ]
]

def get_chatbot_response(message):
    response = chatbot.respond(message)
    if "Let me check the weather" in response:
        location = message.split("in ")[-1]
        weather = get_weather(location)
        if weather:
            return f"The weather in {location} is {weather['description']} with a temperature of {weather['temperature']}°C and humidity of {weather['humidity']}%."
        else:
            return "Sorry, I couldn't fetch the weather for that location."
    return response