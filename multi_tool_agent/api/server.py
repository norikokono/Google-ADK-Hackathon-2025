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
        
        # Input validation
        user_id = data.get('user_id', 'anonymous_user')
        
        # Handle random story request
        if data.get('random', False):
            try:
                # Add error handling to random parameter selection
                genre = random.choice(story_agent._valid_genres or ["fantasy"])
                mood = random.choice(story_agent._valid_moods or ["mysterious"])
                length = random.choice(story_agent._valid_lengths or ["short"])
            except (IndexError, TypeError, ValueError) as e:
                # Fallback if random.choice fails
                logger.error(f"Error selecting random parameters: {e}")
                genre = "fantasy"
                mood = "mysterious"
                length = "short"
            
            logger.debug(f"Random story request: Create a {length} {genre} story with a {mood} mood")
            
            # Create tool request with parameters
            tool_request = ToolRequest(
                user_id=user_id,
                input={
                    'genre': genre,
                    'mood': mood,
                    'length': length
                }
            )
        else:
            # These parameters need to be present in the request
            genre = data.get("genre")
            mood = data.get("mood") 
            length = data.get("length")
            
            # Log the received data
            logger.debug(f"Story request from {user_id}: genre={genre}, mood={mood}, length={length}")
            
            # Option 1: Send as a dictionary (preferred)
            tool_request = ToolRequest(
                user_id=user_id, 
                input={
                    "genre": genre,
                    "mood": mood,
                    "length": length
                }
            )

            # OR Option 2: Send as a pipe-separated string
            # input_prompt = f"{genre}|{mood}|{length}"
            # tool_request = ToolRequest(
            #    user_id=user_id, 
            #    input=input_prompt
            # )
        
        # Process the request with the story agent
        result = story_agent.process(tool_request)
        
        # Error checking - ensure we have a valid result
        if not result or not hasattr(result, 'output'):
            logger.error("StoryAgent returned invalid response")
            return {"success": False, "message": "Failed to generate story"}
            
        # Add try/except for dictionary access
        try:
            # Return the story and parameters
            response = {
                "success": True,
                "story": result.output,
                "parameters": {
                    # Ensure parameters always have values
                    "genre": genre or "fantasy",
                    "mood": mood or "mysterious",
                    "length": length or "short"
                }
            }
            return response
        except Exception as e:
            logger.error(f"Error processing StoryAgent response: {e}")
            return {"success": False, "message": "Failed to process story response"}
    
    except Exception as e:
        logger.error(f"StoryAgent error: {e}")
        return {"success": False, "message": "Error generating story"}

@app.post("/api/chat")
async def chat(request: Request):
    data = await request.json()
    user_input = data.get('input', '')
    user_id = data.get('user_id', 'anonymous_user')
    
    logger.debug(f"Chat request from {user_id}: '{user_input}'")
    
    if not user_input:
        return {
            "success": False, 
            "output": "I didn't receive any input. What would you like to talk about?"
        }
    
    # Create a tool request
    tool_request = ToolRequest(user_id=user_id, input=user_input)
    
    # Import manager here to avoid circular imports
    from ..agents.manager import manager
    
    # Process with manager
    response = manager.process_message(user_id, tool_request)
    
    # Debug the response BEFORE returning it
    logger.debug(f"FULL RESPONSE: output={response.output}, message={response.message}")
    
    return {
        "success": response.success,
        "output": response.output,
        "message": response.message  # Make sure this line exists!
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

def main():
    import uvicorn
    uvicorn.run("multi_tool_agent.api.server:app", host="0.0.0.0", port=8000, reload=True)

if __name__ == "__main__":
    main()