from flask import Flask, request, jsonify
import google.generativeai as genai
import os
import requests
import json


app = Flask(__name__)

# ✅ Set your Gemini API Key from environment variable (recommended)
#genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

# ✅ Choose Gemini 2.5 Flash (fast, cheaper) or Pro (better reasoning)
MODEL = "gemini-2.5-flash"

@app.route("/chat", methods=["POST"])
def chat():
    try:
        user_input = request.json.get("message", "")
        if not user_input:
            return jsonify({"error": "No input provided"}), 400

        #model = genai.GenerativeModel(MODEL)
        #
        #response = model.generate_content(user_input)

        url = "https://generativelanguage.googleapis.com/v1/models/gemini-2.5-flash:generateContent?key=AIzaSyAogr6rekPdx29scGEtE9Msqn_SQ3coLGI"

        payload = json.dumps({
        "contents": [
            {
            "parts": [
                {
                "text": user_input
                }
            ]
            }
        ]
        })
        headers = {
        'Content-Type': 'application/json'
        }
        print(payload)

        response = requests.request("POST", url, headers=headers, data=payload)




        return jsonify({"response": response.text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
