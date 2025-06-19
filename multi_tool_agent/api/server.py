import os
import logging
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse  # Add this import
from pydantic import BaseModel
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
import random

# Load environment variables from project root
load_dotenv(dotenv_path=os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)  # Changed from INFO to DEBUG

# Configure Google Generative AI
import google.generativeai as genai
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)
    logger.info("Google Generative AI configured successfully.")
else:
    logger.critical("GOOGLE_API_KEY environment variable not found. LLM calls will fail. "
                    "Ensure GOOGLE_API_KEY is set in your environment variables or .env file.")

# Import your agent
from ..agents.story import StoryAgent
from ..models.schemas import ToolRequest, ToolResponse
from ..agents.profile import ProfileAgent  # New import

app = FastAPI()

# Allow all origins for development (customize for production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or specify your frontend URL(s)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

story_agent = StoryAgent()
profile_agent = ProfileAgent(model_name="gemini-1.5-flash")  # Ensure profile agent is initialized

class StoryRequest(BaseModel):
    user_id: str
    genre: str
    mood: str
    length: str

@app.post("/api/story/create")
async def create_story(request: Request):
    try:
        data = await request.json()
        user_id = data.get('user_id', 'anonymous_user')
        genre = data.get('genre', '')
        mood = data.get('mood', '')
        length = data.get('length', 'short')
        
        logger.debug(f"Story request from {user_id}: genre={genre}, mood={mood}, length={length}")
        
        # Use only the parameters that _generate_story actually accepts
        story = story_agent._generate_story(
            genre=genre,
            mood=mood,
            length=length,
            user_id=user_id
            # Remove characters and plot_elements parameters
        )
        
        # Return the complete story response
        return {
            "success": True,
            "output": story,
            "story": story,
            "title": data.get('title', f"{mood.capitalize()} {genre.capitalize()} Tale"),
            "isComplete": True
        }
        
    except Exception as e:
        logger.error(f"StoryAgent error: {e}", exc_info=True)
        return {
            "success": False,
            "output": "Sorry, I couldn't create a story right now. Please try again.",
            "message": str(e)
        }

@app.post("/api/chat")
async def chat(request: Request):
    try:
        data = await request.json()
        user_input = data.get('input', '') or data.get('message', '')
        user_id = data.get('user_id', 'anonymous_user')
        
        logger.debug(f"Chat request from {user_id}: '{user_input}'")
        
        if not user_input or user_input.strip() == "":
            return JSONResponse(
                status_code=400,
                content={
                    "success": False,
                    "output": "Hello! I'm PlotBuddy. Please send a message to start our conversation.",
                    "error": "empty_message"
                }
            )
        
        # Create tool request
        tool_request = ToolRequest(user_id=user_id, input=user_input)
        
        # Import orchestrator here to avoid circular imports
        from ..agents.orchestrator import orchestrator
        
        # Let the orchestrator handle all intent detection and routing
        response = orchestrator.process_message(user_id, tool_request)
        
        # Debug the response
        logger.debug(f"FULL RESPONSE: output={response.output}, message={response.message}")
        
        # Check for the story redirect signal
        if response.message == "REDIRECT_TO_STORY_CREATOR":
            return {
                "success": True,
                "output": response.output,
                "message": response.message,
                "action": "navigate_to_story_creator"  # Add this field for the frontend
            }
        
        # Return a normal response
        return {
            "success": response.success,
            "output": response.output,
            "message": response.message
        }
    
    except Exception as e:
        logger.error(f"Chat error: {e}")
        return {
            "success": False, 
            "output": "Sorry, an error occurred. Please try again."
        }

@app.post("/api/profile")
async def get_profile(request: Request):  # Use FastAPI Request
    try:
        # Get data from request
        data = await request.json()  # Use await with FastAPI request
        user_id = data.get('user_id', 'default')
        
        # Use ProfileAgent to get profile data
        from ..agents.profile import ProfileAgent
        profile_agent = ProfileAgent()
        
        # Get the user profile
        user_profile = profile_agent._get_user_profile(user_id)
        
        # Return directly - FastAPI will handle the JSON conversion
        return user_profile
        
    except Exception as e:
        logger.error(f"Profile error: {e}")
        return {
            "error": str(e),
            "subscription": "Free Trial",  # Fallback data
            "stories_remaining": 2, 
            "created_stories": 0,
            "member_since": "2024",
            "favorite_genres": ["Fantasy", "Mystery"]
        }

@app.post("/api/debug")
async def debug_greeting():
    """Debug endpoint to test direct greeting agent calls."""
    from ..agents.greeting import GreetingAgent
    agent = GreetingAgent()
    request = ToolRequest(user_id="test_user", input="hi")
    response = agent.process(request)
    return {"success": response.success, "output": response.output, "message": response.message}

@app.post("/api/profile/brainstorm")
async def profile_brainstorm(request: Request):
    """Endpoint for brainstorming ideas with the profile agent."""
    try:
        data = await request.json()
        genre = data.get('genre', '')
        mood = data.get('mood', '')
        length = data.get('length', '')
        
        # Create a request object for the profile agent
        tool_request = ToolRequest(
            input=f"I need brainstorming help for a {mood} {genre} story of {length} length",
            user_id=data.get('userId', 'anonymous'),
            context={"brainstorm": True, "genre": genre, "mood": mood, "length": length}
        )
        
        # Process with profile agent
        response = profile_agent.process(tool_request)
        
        return {"success": response.success, "output": response.output}
    except Exception as e:
        logger.exception(f"Error in profile brainstorming: {e}")
        return {"success": False, "output": "Sorry, I encountered an error while brainstorming."}

@app.post("/api/profile/advice")
async def profile_advice(request: Request):
    """Endpoint for getting contextual advice from the profile agent."""
    try:
        data = await request.json()
        context = data.get('context', '')
        genre = data.get('genre', '')
        mood = data.get('mood', '')
        
        # Create a request object for the profile agent
        tool_request = ToolRequest(
            input=f"Give me advice about creating a {mood} {genre} story",
            user_id=data.get('userId', 'anonymous'),
            context={"advice": True, "context": context, "genre": genre, "mood": mood}
        )
        
        # Process with profile agent
        response = profile_agent.process(tool_request)
        
        return {"success": response.success, "output": response.output}
    except Exception as e:
        logger.exception(f"Error in profile advice: {e}")
        return {"success": False, "output": "Sorry, I encountered an error while providing advice."}

@app.post("/api/ai/recommendations")
async def ai_recommendations(request: Request):
    try:
        data = await request.json()
        user_id = data.get('user_id', 'anonymous_user')
        content_type = data.get('contentType', 'genre')  # What kind of recommendations (genre, mood, etc.)
        current_selection = data.get('currentSelection', {})  # User's current choices
        
        logger.debug(f"AI recommendations request from {user_id}: type={content_type}")
        
        # Import recommendation agent or use existing agents
        # You can use orchestrator or a specific agent for recommendations
        from ..agents.orchestrator import orchestrator
        
        # Create a tool request for recommendations
        tool_request = ToolRequest(
            user_id=user_id,
            input=f"recommend {content_type}",
            params={
                "content_type": content_type,
                "current_selection": current_selection
            }
        )
        
        # Process with orchestrator to get recommendations
        # If you have a specialized recommendations agent, use that instead
        response = orchestrator.get_recommendations(content_type, current_selection)
        
        # Return recommendations
        return {
            "success": True,
            "recommendations": [
                # Default recommendations if none available from agent
                {"id": 1, "title": "Default Recommendation 1", "genre": "Fantasy", "mood": "Adventurous"},
                {"id": 2, "title": "Default Recommendation 2", "genre": "Mystery", "mood": "Suspenseful"}
            ]
        }
    except Exception as e:
        logger.error(f"Recommendations error: {e}")
        return {
            "success": False,
            "output": "Sorry, I couldn't fetch recommendations right now. Please try again."
        }

def main():
    import uvicorn
    uvicorn.run("multi_tool_agent.api.server:app", host="0.0.0.0", port=8000, reload=True)

if __name__ == "__main__":
    main()