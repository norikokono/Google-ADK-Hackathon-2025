"""
PlotBuddy Server
Flask server for handling chat requests to the multi-agent system.
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from agent import process_message
import traceback
import logging
from typing import Dict, Any, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)

def handle_chat_request(data: Dict[str, Any]) -> Tuple[Dict[str, Any], int]:
    """Process chat request and return response with status code"""
    user_message = data.get("message", "")
    user_id = data.get("user_id", "default_user")
    
    if not user_message:
        return {
            "status": "error",
            "reply": "Message cannot be empty"
        }, 400
    
    response = process_message(user_id=user_id, message=user_message)
    return {
        "status": "success",
        "reply": response
    }, 200

@app.route("/api/chat", methods=["POST"])
def chat():
    """Handle chat endpoint requests"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                "status": "error",
                "reply": "Request body must contain JSON data"
            }), 400
            
        response, status_code = handle_chat_request(data)
        return jsonify(response), status_code
        
    except Exception as e:
        logger.error("Error in /api/chat route:")
        logger.error(traceback.format_exc())
        return jsonify({
            "status": "error",
            "reply": "An internal server error occurred",
            "detail": str(e) if app.debug else None
        }), 500

if __name__ == "__main__":
    logger.info("Starting PlotBuddy server...")
    app.run(
        host="0.0.0.0",
        port=8000,
        debug=True
    )