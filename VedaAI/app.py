from flask import Flask, request, jsonify, render_template
import requests
import json

app = Flask(__name__, template_folder='frontend.html')


# Load intents.json
with open("intents.json", "r") as file:
    intents_data = json.load(file)

# Azure AI Configuration
AZURE_KEY = "ELR6Cc3VzdGTSSHFcNXsECql9obgLeZg3OheZFni2I0vXcOuQ49KJQQJ99BAACGhslBXJ3w3AAAaACOGVET3"  
AZURE_ENDPOINT = "https://your-azure-endpoint.cognitiveservices.azure.com/"  

def get_key_phrases(user_input):
    """Call Azure Text Analytics API to extract key phrases."""
    url = f"{AZURE_ENDPOINT}text/analytics/v3.1/keyPhrases"
    headers = {"Ocp-Apim-Subscription-Key": AZURE_KEY, "Content-Type": "application/json"}
    data = {"documents": [{"id": "1", "language": "en", "text": user_input}]}
    
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()  # Raise HTTPError for bad responses
        return response.json()["documents"][0].get("keyPhrases", [])
    except Exception as e:
        print(f"Error calling Azure API: {e}")
        return []

def get_response_from_intents(user_input, key_phrases):
    """Search the intents.json data for a matching response."""
    for intent in intents_data["intents"]:
        for pattern in intent["patterns"]:
            if pattern.lower() in user_input.lower() or any(phrase.lower() in pattern.lower() for phrase in key_phrases):
                return intent["responses"]
    return ["Sorry, I couldn't find a remedy for your query. Please try again."]

@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.json.get("input", "").lower()
    key_phrases = get_key_phrases(user_input)  # Extract key phrases
    responses = get_response_from_intents(user_input, key_phrases)

    return jsonify({
        "remedy": responses[0],
        "yoga": responses[1] if len(responses) > 1 else "No yoga recommendation."
    })

@app.route('/')
def index():
    return render_template('frontend.html')

if __name__ == '__main__':
    app.run(debug=True)
