import os
from dotenv import load_dotenv

# Load environment variables from .env if present
load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
import logging
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai

# Load environment variables from .env if present
load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if GOOGLE_API_KEY:
    genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
    logger.info("Google Generative AI configured successfully.")
else:
    logger.critical(
        "GOOGLE_API_KEY environment variable not found. LLM calls will fail. "
        "Ensure GOOGLE_API_KEY is set in your environment variables or .env file."
    )

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        user_message = request.json.get('input')
        user_id = request.json.get('user_id', 'anonymous_user')
        logger.info(f"Received message from {user_id}: {user_message}")

        if not GOOGLE_API_KEY:
            return jsonify({
                "output": "Sorry, the AI service is not available (missing API key).",
                "success": False
            }), 503

        # Example: Use Gemini 1.5 Flash Latest (update model as needed)
        model = genai.GenerativeModel("gemini-1.5-flash-latest")
        response = model.generate_content(user_message)
        output = response.text if hasattr(response, "text") else str(response)

        return jsonify({
            "output": output,
            "success": True
        })
    except Exception as e:
        logger.exception("Error in /api/chat endpoint")
        return jsonify({
            "output": f"Server error: {str(e)}",
            "success": False
        }), 500

if __name__ == '__main__':
    app.run(debug=True)