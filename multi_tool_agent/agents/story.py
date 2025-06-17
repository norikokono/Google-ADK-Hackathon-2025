import os
from dotenv import load_dotenv
# Try with explicit path to .env file
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))

import logging
# Set to INFO level to silence DEBUG messages
logging.getLogger(__name__).setLevel(logging.INFO)

from typing import List, Dict, Any
import google.generativeai as genai

from ..models.schemas import ToolRequest, ToolResponse, StoryParameters
from google.adk.agents import LlmAgent

logger = logging.getLogger(__name__)

# Add missing imports at the top of story.py
try:
    from . import client
    logger.debug("Successfully imported client utilities.")
except ImportError:
    logger.warning("Could not import client utilities.")
    client = None

from multi_tool_agent.config.response import GREETING_RESPONSES, FAQ_RESPONSES, STORY_TEMPLATES, ERROR_MESSAGES

class StoryAgent(LlmAgent):
    """
    An AI-powered agent that crafts unique fictional stories based on user-defined parameters.
    It leverages an LlmAgent for generation, validates inputs, and handles common LLM errors.
    """

    def __init__(self, model_name: str = "gemini-2.0-flash"):
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

        # Initialize valid parameters with defaults if not already set
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
        
        # Length descriptions for prompts
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

    def process(self, request: ToolRequest) -> ToolResponse:
        """Process story generation requests"""
        logger.debug(f"StoryAgent processing request for user {request.user_id}.")
        
        try:
            # Handle simple "story" requests
            if isinstance(request.input, str) and request.input.lower().strip() in ["story", "stories", "tell me a story", "write a story"]:
                guide_message = """To create a story, please provide these details:
                
- Genre (like fantasy, sci-fi, mystery)
- Mood (like mysterious, cheerful, dark)
- Length (micro, short, medium, long)

You can say: "Create a mysterious sci-fi micro story" or use the story creation form."""
                return ToolResponse(success=True, output=guide_message)

            # For structured input with parameters
            try:
                if isinstance(request.input, dict):
                    # If it's already a dictionary, validate it
                    genre = request.input.get('genre', '')
                    mood = request.input.get('mood', '')
                    length = request.input.get('length', '')
                    
                    if not all([genre, mood, length]):
                        return ToolResponse.error("Please provide genre, mood, and length for your story.")
                        
                    # Call custom generation method
                    story = self._generate_story(genre, mood, length, request.user_id)
                    
                    # ADD THIS: Check for errors and use fallback
                    if story.startswith("Error:") or story.startswith("Story generation failed:"):
                        logger.warning(f"Using fallback story due to error: {story}")
                        story = self._get_fallback_story(genre, mood, length)
                    
                    # Make sure we return a valid response with the required fields
                    return ToolResponse(
                        success=True, 
                        output=story,
                        # Match the expected structure
                        parameters={
                            "genre": genre,
                            "mood": mood, 
                            "length": length
                        }
                    )
                    
                # Handle string format with | separators
                elif isinstance(request.input, str) and "|" in request.input:
                    parts = [part.strip() for part in request.input.split("|", 2)]
                    if len(parts) >= 3:
                        genre = parts[0]
                        mood = parts[1]
                        length = parts[2]
                        
                        # Call custom generation method
                        story = self._generate_story(genre, mood, length, request.user_id)
                        return ToolResponse(success=True, output=story)
                    else:
                        return ToolResponse.error("Please provide genre, mood, and length separated by '|'")
                else:
                    # Not structured properly
                    return ToolResponse.error("To create a story, please provide genre, mood, and length.")
                    
            except Exception as e:
                logger.error(f"Error processing story parameters: {e}")
                return ToolResponse.error(f"Error processing story parameters: {str(e)}")
                
        except Exception as e:
            logger.error(f"Error generating story: {e}")
            return ToolResponse.error("Sorry, I encountered an error creating your story.")
            
    def _generate_story(self, genre: str, mood: str, length: str, user_id: str) -> str:
        """Generate a story based on the provided parameters"""
        logger.info(f"Generating {length} {mood} {genre} story for {user_id}")
        
        try:
            # Get the story content
            story = self._generate_story_with_llm(genre, mood, length, user_id)
            
            # Clean up any titles the LLM might have added
            lines = story.splitlines()
            first_line = lines[0] if lines else ""
            
            if (first_line.startswith('#') or 
                (len(first_line) < 60 and 
                 (genre.lower() in first_line.lower() or 
                  mood.lower() in first_line.lower() or 
                  "story" in first_line.lower() or
                  "tale" in first_line.lower()))):
                story = '\n'.join(lines[1:]).strip()
            
            # DYNAMIC EMOJIS based on genre and mood
            genre_emojis = {
                "mystery": "🔍 🕵️ 🧩",
                "scifi": "🚀 👽 🛸",
                "fantasy": "🧙 🐉 ✨",
                "romance": "❤️ 💘 💞",
                "adventure": "🧭 🏝️ 🏔️",
                "horror": "👻 🧟 🔪",
                "comedy": "😂 🤣 🎭",
                "thriller": "🔫 🕵️ 🔦",
                "historical": "📜 ⏳ 🏛️",
                "western": "🤠 🐎 🌵",
                "cyberpunk": "🤖 💻 🌃"
            }
            
            mood_emojis = {
                "mysterious": "🔮 🌌 🧿",
                "whimsical": "🦄 🌈 🧚",
                "dark": "🖤 🌑 🌚",
                "romantic": "💖 💓 💗",
                "epic": "🏆 ⚔️ 🛡️",
                "funny": "😆 🤹 🎪",
                "melancholic": "😢 🌧️ 🥀",
                "suspenseful": "⏳ 🔪 🚪", 
                "nostalgic": "🕰️ 📷 🎞️",
                "dreamy": "💫 🌙 ☁️",
                "tense": "😰 ⚡ 💢",
                "peaceful": "🕊️ 🌿 🍃"
            }
            
            length_emojis = {
                "micro": "📝",
                "short": "📖",
                "medium": "📕",
                "long": "📚",
                "epic poem": "📜📜"  
            }
            
            # Get emojis or use defaults
            g_emoji = genre_emojis.get(genre.lower(), "✨")[:1]  # Take just the first emoji
            m_emoji = mood_emojis.get(mood.lower(), "✨")[:1]
            l_emoji = length_emojis.get(length.lower(), "📄")
            
            # Create a dynamic title with the most relevant emoji
            title = f"{g_emoji} {genre.title()}: A {mood.title()} {length.title()} Tale {m_emoji}"
            
            # Format with a prettier header and footer using relevant emojis
            formatted_story = f"""{title}

{story}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{g_emoji} Genre: {genre.title()}
{m_emoji} Mood: {mood.title()}
{l_emoji} Length: {length.title()}
"""
            return formatted_story.strip()
            
        except Exception as e:
            logger.error(f"Error in story generation logic: {e}")
            return "Error in story generation logic."
        
    def _generate_story_with_llm(self, genre: str, mood: str, length: str, user_id: str) -> str:
        """Generate story content using the LLM based on provided parameters"""
        logger.info(f"Initiating LLM call for user {user_id}: Genre='{genre}', Mood='{mood}', Length='{length}'.")

        # Ensure key from client module is used if available
        if client and hasattr(client, 'GOOGLE_API_KEY') and client.GOOGLE_API_KEY:
            os.environ["GOOGLE_GENERATIVE_AI_API_KEY"] = client.GOOGLE_API_KEY
            genai.configure(api_key=client.GOOGLE_API_KEY)
            logger.info("Using API key from client module")
        
        # Debug environment variables
        logger.debug(f"Environment variables: {list(os.environ.keys())}")
        api_key = os.environ.get("GOOGLE_GENERATIVE_AI_API_KEY")
        logger.debug(f"API key found: {bool(api_key)}")
        
        # Retry mechanism for API key loading
        attempt = 0
        max_retries = 3

        while attempt < max_retries:
            attempt += 1
            api_key = os.environ.get("GOOGLE_GENERATIVE_AI_API_KEY")
            
            if api_key:
                break
            
            logger.warning(f"API key not found, attempt {attempt}/{max_retries}, retrying...")
            # Force reload environment vars
            load_dotenv()
            time.sleep(1)  # Brief pause between retries

        if not api_key:
            logger.error(f"Missing Google Generative AI API key after {max_retries} attempts")
            return self._get_fallback_story(genre, mood, length)
        
        # Get word count guidance based on length
        length_description = self._length_descriptions.get(
            length.lower(), 
            "a moderate length story (around 750-1000 words)"
        )

        # Create a detailed prompt for better quality stories
        prompt = f"""Write a {mood} {genre} story that is {length_description}
    
    Your story should:
    - Have a compelling {mood} atmosphere throughout
    - Follow {genre} genre conventions
    - Include well-developed characters
    - Have a clear beginning, middle, and end
    - Be creative and original
    
    Remember: Do NOT include a title. Start directly with the story text.
    """
    
        # Check if API key is configured
        api_key = os.environ.get("GOOGLE_GENERATIVE_AI_API_KEY")
        if not api_key:
            logger.error("Missing Google Generative AI API key")
            return "Error: Missing API key for story generation."
        
        # Initialize the generative model with our base configuration
        model = genai.GenerativeModel(
            model_name=self.model,
            generation_config=self._generation_config_base
        )
        
        # Generate the story with timeout handling
        try:
            response = model.generate_content(prompt)
            
            # Check if response is None
            if response is None:
                logger.error("Received None response from generative model")
                return "Error: No response received from the AI model."
            
            # Extract and return just the text content
            if hasattr(response, 'text'):
                story_text = response.text
                if not story_text:
                    return "Error: Generated story was empty."
                return story_text
            else:
                # Safely convert response to string
                return str(response)
                
        except Exception as gen_error:
            logger.error(f"Content generation error: {gen_error}")
            return f"Story generation failed: {str(gen_error)}"
            
    def _get_fallback_story(self, genre: str, mood: str, length: str) -> str:
        """Provide a fallback story when API generation fails"""
        
        # Very short fallback stories for common genres
        fallbacks = {
            "mystery": "The detective stared at the empty room. Something wasn't right - the dust patterns were disturbed, but nothing was missing. Then he noticed it: the shadow without an owner.",
            "scifi": "The colony ship's AI woke me early. 'We've found something,' it said. Outside my window was a planet that shouldn't exist, with lights blinking in a perfect grid pattern.",
            "fantasy": "The dragon lowered its massive head. 'You're the first human to speak our language in centuries,' it said. 'Perhaps you're the one from the prophecy after all.'",
            "romance": "Our hands touched reaching for the same book. When our eyes met, time seemed to pause. 'I've been looking for that book for years,' she said with a smile that changed everything.",
            "horror": "The messages kept coming from my brother's phone. Simple things like 'How's your day?' and 'Miss you.' The problem was, we'd buried him with that phone yesterday."
        }
        
        # Return a matching fallback or generic message
        return fallbacks.get(genre.lower(), 
            "The story begins in your imagination. While our AI storyteller takes a short break, "
            "perhaps you can start crafting your own tale? We'll be back online shortly.")