import os
from dotenv import load_dotenv

# Your existing load_dotenv call:
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))

# --- Add this for debugging ---
print(f"DEBUG: GOOGLE_API_KEY from os.environ: {os.environ.get('GOOGLE_API_KEY')}")
# --- End debug ---

import logging
import os
from dotenv import load_dotenv
from typing import Dict, Any

# Ensure google-adk is installed: pip install google-adk
from google.adk.agents import LlmAgent
# If you plan to use genai directly *outside* of what LlmAgent handles, keep this
import google.generativeai as genai 

# Assuming these are in your project.
# For a standalone example, you might need to mock or define them simply.
# from ..models.schemas import ToolRequest, ToolResponse, StoryParameters

# Mock classes for demonstration if your actual files are not accessible
class ToolRequest:
    def __init__(self, input: Any, user_id: str = "test_user"):
        self.input = input
        self.user_id = user_id

class ToolResponse:
    def __init__(self, success: bool, output: str, parameters: Dict[str, Any] = None, message: str = None):
        self.success = success
        self.output = output
        self.parameters = parameters if parameters is not None else {}
        self.message = message

    @classmethod
    def error(cls, message: str):
        return cls(success=False, output=message)


# Load environment variables from .env
# This path might need adjustment depending on where your .env is relative to this script.
# It's good practice to ensure the .env is loaded early.
# os.path.dirname(os.path.dirname(__file__)) assumes .env is one level up from the directory
# containing this script. Adjust if your .env is in a different location.
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# This client module would typically hold shared configurations, like a global API key.
# If `client.GOOGLE_API_KEY` is meant to be the primary way to get the key,
# ensure it's correctly populated.
try:
    from . import client
    if hasattr(client, 'GOOGLE_API_KEY') and client.GOOGLE_API_KEY:
        os.environ["GOOGLE_API_KEY"] = client.GOOGLE_API_KEY
        logger.info("GOOGLE_API_KEY loaded from client module.")
except ImportError:
    client = None
    logger.info("Client module not found, relying on direct environment variable for API key.")

# It's good to print the key status early for debugging
print("GOOGLE_API_KEY in script startup:", os.environ.get("GOOGLE_API_KEY"))


# Assuming these are correctly set up in your project structure
# from multi_tool_agent.config.response import GREETING_RESPONSES, FAQ_RESPONSES, STORY_TEMPLATES, ERROR_MESSAGES
# Mock these for runnable example
GREETING_RESPONSES = []
FAQ_RESPONSES = []
STORY_TEMPLATES = []
ERROR_MESSAGES = {}


class StoryAgent(LlmAgent):
    """
    An AI-powered agent that crafts unique fictional stories based on user-defined parameters.
    It leverages an LlmAgent for generation, validates inputs, and handles common LLM errors.
    """

    def __init__(self, model_name: str = "gemini-2.0-flash"):
        # The LlmAgent constructor is where you define the model it will use.
        # ADK then manages the connection to this model.
        super().__init__(
            model=model_name,
            name="story_generation_agent",
            description="A creative assistant that generates unique fictional stories "
                        "based on specified genre, mood, and length.",
            instruction=(
                "You are PlotBuddy, an expert creative writing AI assistant. "
                "Your core task is to generate compelling, original fictional stories according to user specifications. "
                "You will be provided with a genre, mood, and desired length. "
                "Your output should *only* be the story text, without any conversational preamble, "
                "titles, or concluding remarks unless explicitly requested within the story's prompt. "
                "Adhere strictly to the genre, mood, and length constraints."
            )
        )

        self._valid_genres = [
            "fantasy", "scifi", "mystery", "romance", "horror", 
            "adventure", "thriller", "comedy", "drama", "historical"
        ]
        self._valid_moods = [
            "mysterious", "suspenseful", "romantic", "dark", "whimsical",
            "epic", "melancholic", "hopeful", "tense", "peaceful"
        ]
        self._valid_lengths = [
            "micro", "short", "medium", "long"
        ]
        self._length_descriptions = {
            "micro": "very short (around 100-200 words)",
            "short": "brief (around 300-500 words)",
            "medium": "moderate length (around 750-1000 words)",
            "long": "detailed (around 1500-2000 words)"
        }
        self._generation_config_base: Dict[str, Any] = {
            "temperature": 0.85,
            "top_p": 0.95,
            "top_k": 40,
        }
        logger.info("StoryAgent initialized.")

    def process(self, request: ToolRequest, context: dict = None) -> ToolResponse:
        logger.info(f"StoryAgent process called with request: {request.input}")
        try:
            if isinstance(request.input, str) and request.input.lower().strip() in ["story", "stories", "tell me a story", "write a story"]:
                guide_message = """To create a story, please provide these details:
                
- Genre (like fantasy, sci-fi, mystery)
- Mood (like mysterious, cheerful, dark)
- Length (micro, short, medium, long)

You can say: "Create a mysterious sci-fi micro story" or use the story creation form."""
                return ToolResponse(success=True, output=guide_message)

            try:
                if isinstance(request.input, dict):
                    genre = request.input.get('genre', '')
                    mood = request.input.get('mood', '')
                    length = request.input.get('length', '')
                    
                    if not all([genre, mood, length]):
                        return ToolResponse.error("Please provide genre, mood, and length for your story.")
                        
                    story, used_fallback = self._generate_story(genre, mood, length, request.user_id)
                    if used_fallback:
                        notice = (
                            "⚠️ Note: Our AI story service is temporarily unavailable. "
                            "Here's a sample story instead:\n\n"
                        )
                        return ToolResponse(
                            success=True,
                            output=notice + story,
                            parameters={"genre": genre, "mood": mood, "length": length},
                            message="LLM_UNAVAILABLE_FALLBACK"
                        )
                    return ToolResponse(
                        success=True,
                        output=story,
                        parameters={"genre": genre, "mood": mood, "length": length}
                    )
                elif isinstance(request.input, str) and "|" in request.input:
                    parts = [part.strip() for part in request.input.split("|", 2)]
                    if len(parts) >= 3:
                        genre = parts[0]
                        mood = parts[1]
                        length = parts[2]
                        story, used_fallback = self._generate_story(genre, mood, length, request.user_id)
                        if used_fallback:
                            notice = (
                                "⚠️ Note: Our AI story service is temporarily unavailable. "
                                "Here's a sample story instead:\n\n"
                            )
                            return ToolResponse(
                                success=True,
                                output=notice + story,
                                parameters={"genre": genre, "mood": mood, "length": length},
                                message="LLM_UNAVAILABLE_FALLBACK"
                            )
                        return ToolResponse(success=True, output=story)
                    else:
                        return ToolResponse.error("Please provide genre, mood, and length separated by '|'")
                else:
                    return ToolResponse.error("To create a story, please provide genre, mood, and length.")
                    
            except Exception as e:
                logger.error(f"Error processing story parameters: {e}", exc_info=True)
                return ToolResponse.error(f"Error processing story parameters: {str(e)}")
                
        except Exception as e:
            logger.error(f"Error generating story: {e}", exc_info=True)
            return ToolResponse.error("Sorry, I encountered an error creating your story.")

    def _generate_story(self, genre: str, mood: str, length: str, user_id: str):
        """Generate a story based on the provided parameters. Returns (story, used_fallback: bool)"""
        logger.info(f"Generating {length} {mood} {genre} story for {user_id}")
        used_fallback = False
        try:
            # Try LLM
            story = self._generate_story_with_llm(genre, mood, length, user_id)
            if story.startswith("Error") or "unavailable" in story.lower():
                raise RuntimeError("LLM unavailable or failed to produce valid content.")
        except Exception as e:
            logger.warning(f"LLM unavailable or failed: {e}", exc_info=True)
            story = self._get_fallback_story(genre, mood, length)
            used_fallback = True

        # Emojis for formatting
        genre_emojis = {
            "mystery": "🔍", "scifi": "🚀", "fantasy": "🧙", "romance": "❤️", 
            "horror": "👻", "adventure": "🧭", "thriller": "🔫", 
            "comedy": "😂", "drama": "🎭", "historical": "📜"
        }
        mood_emojis = {
            "mysterious": "🔮", "whimsical": "🦄", "dark": "🖤", 
            "romantic": "💖", "epic": "🏆", "funny": "😆", 
            "melancholic": "😢", "suspenseful": "⏳", "hopeful": "🌅", 
            "tense": "😰", "peaceful": "🕊️"
        }
        length_emojis = {
            "micro": "📝", "short": "📖", "medium": "📕", "long": "📚"
        }
        g_emoji = genre_emojis.get(genre.lower(), "✨")
        m_emoji = mood_emojis.get(mood.lower(), "✨")
        l_emoji = length_emojis.get(length.lower(), "📄")

        title = f"{g_emoji} {genre.title()}: A {mood.title()} {length.title()} Tale {m_emoji}"

        formatted_story = f"""{title}

{story}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{g_emoji} Genre: {genre.title()}
{m_emoji} Mood: {mood.title()}
{l_emoji} Length: {length.title()}
"""
        return formatted_story.strip(), used_fallback

    def _generate_story_with_llm(self, genre: str, mood: str, length: str, user_id: str) -> str:
        """Generate story content using the LLM based on provided parameters"""
        logger.info(f"Initiating LLM call for user {user_id}: Genre='{genre}', Mood='{mood}', Length='{length}'.")

        # ADK's LlmAgent base class should ideally handle the model configuration.
        # However, if you need explicit genai.configure, ensure the API key is available.
        api_key = os.environ.get("GOOGLE_API_KEY")
        if not api_key:
            logger.error("Missing Google Generative AI API key in environment variables.")
            return "Error: Missing API key for story generation."
        
        # This call might be redundant if ADK's LlmAgent setup already configures genai.
        # However, keeping it here ensures it's configured if ADK's internal mechanism
        # isn't explicitly doing it or if running this method standalone.
        genai.configure(api_key=api_key) 
        
        length_description = self._length_descriptions.get(
            length.lower(), 
            "a moderate length story (around 750-1000 words)"
        )

        prompt = f"""Write a {mood} {genre} story that is {length_description}
Your story should:
- Have a compelling {mood} atmosphere throughout
- Follow {genre} genre conventions
- Include well-developed characters
- Have a clear beginning, middle, and end
- Be creative and original

Remember: Do NOT include a title. Start directly with the story text.
"""
        print("DEBUG: Starting story generation with ADK LlmAgent")
        print("DEBUG: API key status (should be present):", bool(api_key))
        print("DEBUG: Prompt is", prompt[:100] + "...") # Truncate for cleaner debug output
        print("DEBUG: API key before LLM call:", os.environ.get("GOOGLE_API_KEY"))

        try:
            print(f"DEBUG: About to call Gemini API using model: {self.model}")
            # Use the model attribute from the LlmAgent base class
            model = genai.GenerativeModel(
                model_name=self.model,
                generation_config=self._generation_config_base
            )
            response = model.generate_content(prompt)
            print("DEBUG: Gemini API raw response (truncated):", str(response)[:100] + "...")
            logger.info(f"Gemini API raw response: {response}")

            if response is None or not hasattr(response, 'text') or not response.text:
                logger.error("Received empty or invalid response from generative model.")
                return "Error: No valid response received from the AI model."
            
            story_text = response.text
            logger.info(f"Generated story text (truncated): {story_text[:50]}...")
            return story_text

        except Exception as gen_error:
            print("DEBUG: Gemini API error:", gen_error)
            logger.error(f"Content generation error: {gen_error}", exc_info=True)
            error_str = str(gen_error).lower()
            # Provide a clear user-facing error if Gemini API is not working
            if "quota" in error_str or "violation" in error_str or "policy" in error_str or "rate limit" in error_str:
                return "Sorry, the Gemini API is not working due to quota or policy violation. Please try again later."
            if "resource exhausted" in error_str or "internal error" in error_str:
                return "Sorry, the Gemini API is currently overloaded or experiencing an internal issue. Please try again in a moment."
            return f"Sorry, the Gemini API is not working: {str(gen_error)}. Please check your API key and try again."

    def _get_fallback_story(self, genre: str, mood: str, length: str) -> str:
        """Provide a fallback story when API generation fails, formatted as requested."""
        fallbacks = {
            "mystery": "The detective stared at the empty room. Something wasn't right—the dust patterns were disturbed, but nothing was missing. Then he noticed it: the shadow without an owner.",
            "scifi": "The colony ship's AI woke me early. 'We've found something,' it said. Outside my window was a planet that shouldn't exist, with lights blinking in a perfect grid pattern.",
            "fantasy": "The dragon lowered its massive head. 'You're the first human to speak our language in centuries,' it said. 'Perhaps you're the one from the prophecy after all.'",
            "romance": "Our hands touched reaching for the same book. When our eyes met, time seemed to pause. 'I've been looking for that book for years,' she said with a smile that changed everything.",
            "horror": "The messages kept coming from my brother's phone. Simple things like 'How's your day?' and 'Miss you.' The problem was, we'd buried him with that phone yesterday.",
            "adventure": "The map led us to the edge of the world, where waterfalls spilled into clouds. 'Ready?' she asked, grinning. I nodded, heart pounding with the promise of the unknown.",
            "comedy": "The chicken didn't cross the road. It checked its calendar, realized it was Tuesday, and went back to bed.",
            "thriller": "The phone rang at midnight. 'Run,' whispered the voice. I didn't ask who it was—I just ran.",
            "historical": "The parchment crackled as she unrolled it. Centuries of secrets waited in faded ink, promising to change everything she thought she knew.",
            "drama": "He stood in the rain, letter in hand, as the city lights blurred into tears. Tonight, everything would change."
        }
        story = fallbacks.get(genre.lower(), 
            "Once upon a time, in a world of endless possibilities, a new adventure began...")
        return story

# Instantiate the agent. ADK will use the 'model' parameter passed to LlmAgent's super().__init__.
story_agent = StoryAgent()

# To run this in an ADK context, you'd typically have an app.py like this:
# from google.adk.app import AdkApp
# from your_module_name import story_agent # Assuming this file is your_module_name.py
#
# app = AdkApp(agents={"story_agent": story_agent})
#
# if __name__ == "__main__":
#     app.run()
#
# You would then run `adk web` or `adk run` from your terminal in the directory
# where your `app.py` or agent definition is.