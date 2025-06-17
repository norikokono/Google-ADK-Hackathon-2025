import os
import logging
import google.generativeai as genai
from flask import Flask, request, jsonify

app = Flask(__name__)

logger = logging.getLogger(__name__)

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)
    logger.info("Google Generative AI configured successfully.")
else:
    logger.critical(
        "GOOGLE_API_KEY environment variable not found. LLM calls will fail. "
        "Ensure GOOGLE_API_KEY is set in your environment variables or .env file."
    )

@app.route('/api/chat', methods=['POST'])
def chat():
    user_message = request.json.get('input')
    user_id = request.json.get('user_id', 'anonymous_user')

    logger.info(f"Received message from {user_id}: {user_message}")

    # Here you would add the logic to handle the message,
    # interact with the LLM, and generate a response.
    response_message = "This is the bot's response message"

    return jsonify({
        "output": response_message,
        "success": True
    })

if __name__ == '__main__':
    app.run(debug=True)