import os
import logging
import random
from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware

# Load environment variables from project root
load_dotenv(dotenv_path=os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
print("GOOGLE_API_KEY:", GOOGLE_API_KEY)
if not GOOGLE_API_KEY:
    logger.critical("GOOGLE_API_KEY environment variable not found. LLM calls will fail. "
                    "Ensure GOOGLE_API_KEY is set in your environment variables or .env file.")

# Use absolute imports if possible
from multi_tool_agent.agents.story import StoryAgent
from multi_tool_agent.models.schemas import ToolRequest
from multi_tool_agent.agents.profile import ProfileAgent
from multi_tool_agent.agents.orchestrator import OrchestratorAgent

orchestrator = OrchestratorAgent()

app = FastAPI()

# --- CORS Configuration ---
allowed_origins_str = os.getenv(
    "CORS_ALLOWED_ORIGINS",
    "http://localhost:3000,https://adk-hackathon-2025-b4bfc.web.app"
)
allowed_origins = [origin.strip() for origin in allowed_origins_str.split(',')]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# --- End CORS Configuration ---

def get_story_agent():
    return StoryAgent()

def get_profile_agent():
    return ProfileAgent(model_name="gemini-1.5-flash")

class StoryRequest(BaseModel):
    user_id: str
    genre: str
    mood: str
    length: str

@app.post("/api/story/create")
async def create_story(request: Request, story_agent: StoryAgent = Depends(get_story_agent)):
    try:
        data = await request.json()
        user_id = data.get('user_id', 'anonymous_user')

        if data.get('random', False):
            try:
                genre = random.choice(story_agent._valid_genres or ["fantasy"])
                mood = random.choice(story_agent._valid_moods or ["mysterious"])
                length = random.choice(story_agent._valid_lengths or ["short"])
            except Exception as e:
                logger.error(f"Error selecting random parameters for story creation: {e}")
                genre, mood, length = "fantasy", "mysterious", "short"
            logger.debug(f"Random story request for {user_id}: Create a {length} {genre} story with a {mood} mood")
        else:
            genre = data.get("genre")
            mood = data.get("mood")
            length = data.get("length")
            logger.debug(f"Story request from {user_id}: genre={genre}, mood={mood}, length={length}")

        if not all([genre, mood, length]):
            raise HTTPException(status_code=400, detail="Genre, mood, and length are required for non-random story creation.")

        tool_request = ToolRequest(
            user_id=user_id,
            input={
                "genre": genre,
                "mood": mood,
                "length": length
            }
        )

        result = story_agent.process(tool_request)
        if not result or not hasattr(result, 'output') or not result.success:
            logger.error(f"StoryAgent returned invalid or unsuccessful response for user {user_id}: {result.message if result else 'No result'}")
            return JSONResponse(status_code=500, content={"success": False, "message": result.message if result else "Failed to generate story due to an internal error."})

        response = {
            "success": True,
            "story": result.output,
            "parameters": {
                "genre": genre,
                "mood": mood,
                "length": length
            }
        }
        return JSONResponse(content=response)

    except HTTPException as http_e:
        raise http_e
    except Exception as e:
        logger.exception(f"Unhandled error in create_story endpoint for user {user_id}: {e}")
        return JSONResponse(status_code=500, content={"success": False, "message": "An unexpected error occurred while generating the story."})

@app.post("/api/chat")
async def chat(request: Request):
    try:
        data = await request.json()
        user_input = data.get('input', '')
        user_id = data.get('user_id', 'anonymous_user')
        hour = data.get('hour')
        time_zone = data.get('time_zone')

        context = {}
        if hour is not None:
            context["hour"] = hour
        if time_zone is not None:
            context["time_zone"] = time_zone

        tool_request = ToolRequest(user_id=user_id, input=user_input, context=context)
        response = orchestrator.process(tool_request)
        success = getattr(response, "success", False)
        output = getattr(response, "output", "")
        message = getattr(response, "message", "No message returned from orchestrator.")
        return JSONResponse(
            content={
                "success": success,
                "output": output,
                "message": message
            }
        )
    except Exception as e:
        logger.exception(f"Unhandled error in chat endpoint: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "output": "I'm sorry, I encountered an error. Please try again later.",
                "message": str(e)
            }
        )

@app.post("/api/profile")
async def get_profile(request: Request, profile_agent: ProfileAgent = Depends(get_profile_agent)):
    try:
        data = await request.json()
        user_id = data.get('user_id', 'default')
        user_profile = profile_agent._get_user_profile(user_id)
        return JSONResponse(content=user_profile)
    except Exception as e:
        logger.exception(f"Profile error for user {user_id}: {e}")
        return JSONResponse(status_code=500, content={
            "success": False,
            "error": str(e),
            "subscription": "Free Trial",
            "stories_remaining": 2,
            "created_stories": 0,
            "member_since": "2024",
            "favorite_genres": ["Fantasy", "Mystery"],
            "message": "Failed to load profile. Displaying default data."
        })

@app.post("/api/debug")
async def debug_greeting():
    from multi_tool_agent.agents.greeting import GreetingAgent
    agent = GreetingAgent()
    request = ToolRequest(user_id="test_user", input="hi")
    response = agent.process(request)
    return JSONResponse(content={"success": response.success, "output": response.output, "message": response.message})

@app.post("/api/profile/brainstorm")
async def profile_brainstorm(request: Request, profile_agent: ProfileAgent = Depends(get_profile_agent)):
    try:
        data = await request.json()
        genre = data.get('genre', '')
        mood = data.get('mood', '')
        length = data.get('length', '')
        user_id = data.get('user_id', 'anonymous_user')

        tool_request = ToolRequest(
            input=f"I need brainstorming help for a {mood} {genre} story of {length} length",
            user_id=user_id,
            context={"brainstorm": True, "genre": genre, "mood": mood, "length": length}
        )
        response = profile_agent.process(tool_request)
        return JSONResponse(content={"success": response.success, "output": response.output, "message": response.message})
    except Exception as e:
        logger.exception(f"Error in profile brainstorming for user {user_id}: {e}")
        return JSONResponse(status_code=500, content={"success": False, "output": "Sorry, I encountered an error while brainstorming.", "message": str(e)})

@app.post("/api/profile/advice")
async def profile_advice(request: Request, profile_agent: ProfileAgent = Depends(get_profile_agent)):
    try:
        data = await request.json()
        context_text = data.get('context', '')
        genre = data.get('genre', '')
        mood = data.get('mood', '')
        user_id = data.get('user_id', 'anonymous_user')

        tool_request = ToolRequest(
            input=f"Give me advice about creating a {mood} {genre} story",
            user_id=user_id,
            context={"advice": True, "context": context_text, "genre": genre, "mood": mood}
        )
        response = profile_agent.process(tool_request)
        return JSONResponse(content={"success": response.success, "output": response.output, "message": response.message})
    except Exception as e:
        logger.exception(f"Error in profile advice for user {user_id}: {e}")
        return JSONResponse(status_code=500, content={"success": False, "output": "Sorry, I encountered an error while providing advice.", "message": str(e)})

def main():
    import uvicorn
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run("multi_tool_agent.api.server:app", host="0.0.0.0", port=port)

if __name__ == "__main__":
    main()