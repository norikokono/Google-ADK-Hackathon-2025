import os
from dotenv import load_dotenv
# Try with explicit path to .env file
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))

import logging
# Set to INFO level to silence DEBUG messages
logging.getLogger(__name__).setLevel(logging.INFO)

from typing import List, Dict, Any, ClassVar
import google.generativeai as genai
import re
import json  # Add this import at the top

from ..models.schemas import ToolRequest, ToolResponse
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

    # Define story length categories with word counts and reading times
    STORY_LENGTHS: ClassVar[Dict[str, Dict[str, Any]]] = {
        "micro": {"words": 100, "read_time": "2-3 min"},
        "short": {"words": 500, "read_time": "5-7 min"},
        "medium": {"words": 1000, "read_time": "10-12 min"},
        "long": {"words": 2000, "read_time": "15-20 min"}
    }

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
        prompt = (
            f"As a master storyteller, craft an original, professional-quality {genre} story "
            f"that radiates a distinctly {mood} mood and is {length_description}.\n\n"
            "Guidelines:\n"
            "- Immerse the reader in a vivid, atmospheric setting that exemplifies the chosen mood.\n"
            "- Adhere to the conventions and expectations of the {genre} genre, but avoid clichés—strive for creativity and uniqueness.\n"
            "- Develop memorable, nuanced characters with clear motivations.\n"
            "- Structure the narrative with a strong beginning, engaging middle, and satisfying conclusion.\n"
            "- Employ evocative language, sensory details, and natural dialogue to bring the story to life.\n"
            "- Ensure the story is suitable for a general audience.\n"
            "- Avoid any explicit content, profanity, or sensitive themes.\n"
            "- Focus on storytelling rather than exposition or moralizing.\n"
            "- Keep the story concise and engaging, avoiding unnecessary tangents or filler.\n"
            "- Use a consistent tone that matches the mood and genre throughout the story.\n"
            "- Ensure the story is original and not derivative of existing works.\n"
            "- Do not include any titles, author names, or introductory remarks.\n"
            "- The story should be self-contained and not require any additional context or explanation.\n"     
            f"- Target length: {length_description}.\n"
            "\n"
            "Important: Do NOT include a title or any introductory or closing remarks. Begin immediately with the story text."
        )
    
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
    
    def _extract_story_parameters(self, message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Extract story parameters from the user's message and context."""
        params = {}
        
        # First, use any parameters already in the context
        for param in ["genre", "mood", "style", "length", "theme", "characters"]:
            if param in context:
                params[param] = context[param]
        
        # Then, try to extract from the message if not already set
        # Extract length
        if "length" not in params:
            length_patterns = {
                r"\b(?:micro|tiny|very short|super short|brief|minimal)\b": "micro",
                r"\b(?:short|quick|small)\b": "short",
                r"\b(?:medium|moderate|average)\b": "medium",
                r"\b(?:long|extended|detailed|comprehensive|thorough)\b": "long"
            }
            
            for pattern, length in length_patterns.items():
                if re.search(pattern, message.lower()):
                    params["length"] = length
                    break
        
        # Extract genre if not already set
        if "genre" not in params:
            common_genres = [
                "fantasy", "sci-fi", "science fiction", "mystery", "thriller", 
                "romance", "horror", "historical", "adventure", "comedy",
                "drama", "dystopian", "young adult", "fairy tale", "fable"
            ]
            
            for genre in common_genres:
                if genre.lower() in message.lower():
                    params["genre"] = genre
                    break
        
        # Extract mood if not already set
        if "mood" not in params:
            common_moods = [
                "suspenseful", "uplifting", "dark", "whimsical", "thoughtful", 
                "mysterious", "romantic", "action-packed", "melancholy", "humorous",
                "eerie", "nostalgic", "tense", "inspirational", "peaceful"
            ]
            
            for mood in common_moods:
                if mood.lower() in message.lower():
                    params["mood"] = mood
                    break
        
        return params

    def _is_story_generation_request(self, message: str) -> bool:
        """Determine if the message is requesting story generation."""
        generation_patterns = [
            r"\b(?:generate|create|write|make|give me|produce)\b.+\b(?:story|tale|narrative)\b",
            r"\b(?:tell|write)\b.+\b(?:story|tale|narrative)\b.+\b(?:about|with|featuring)\b",
            r"\b(?:can you|could you|please|would you)\b.+\b(?:write|create)\b.+\b(?:story)\b"
        ]
        
        for pattern in generation_patterns:
            if re.search(pattern, message.lower()):
                return True
                
        return False

    def _provide_story_guidance(self, user_id: str, message: str, params: Dict[str, Any]) -> ToolResponse:
        """Provide guidance on story creation."""
        # Extract any specific guidance areas from message
        guidance_areas = []
        
        guidance_keywords = {
            "character": "character development",
            "plot": "plot structure",
            "setting": "world-building",
            "dialogue": "dialogue writing",
            "pacing": "narrative pacing",
            "ending": "creating satisfying endings",
            "beginning": "crafting engaging openings"
        }
        
        for keyword, area in guidance_keywords.items():
            if keyword in message.lower():
                guidance_areas.append(area)
        
        # Default to general guidance if no specific areas found
        if not guidance_areas:
            guidance_areas = ["general story structure"]
        
        # Get length if specified
        length = params.get("length", "")
        length_guidance = ""
        
        if length in self.STORY_LENGTHS:
            word_count = self.STORY_LENGTHS[length]["words"]
            read_time = self.STORY_LENGTHS[length]["read_time"]
            
            length_guidance = f"""
            For {length} stories (~{word_count} words, {read_time} reading time):
            
            - Structure: {self._get_length_structure_guidance(length)}
            - Character development: {self._get_length_character_guidance(length)}
            - Pacing: {self._get_length_pacing_guidance(length)}
            """
        
        try:
            # Create guidance prompt
            prompt = f"""
            Provide clear, practical guidance on {', '.join(guidance_areas)} for story creation.
            
            User message: {message}
            
            {length_guidance}
            
            Include:
            1. 3-4 specific, actionable techniques
            2. Examples to illustrate key points
            3. Common pitfalls to avoid
            
            Focus on practical advice that can be immediately applied.
            """
            
            # Generate guidance
            model = genai.GenerativeModel(self.model_name)
            response = model.generate_content(prompt)
            guidance = response.text.strip()
            
            return ToolResponse(
                success=True,
                output=guidance
            )
            
        except Exception as e:
            logger.error(f"Error providing story guidance: {e}")
            return ToolResponse(
                success=False,
                output=f"I apologize, but I encountered an issue while creating guidance on {', '.join(guidance_areas)}. Would you like to try a different topic?",
                message=f"Error providing story guidance: {str(e)}"
            )

    def _get_length_structure_guidance(self, length: str) -> str:
        """Get structure guidance specific to story length."""
        guidance = {
            "micro": "Focus on a single moment or scene with maximum impact. Use a clear setup and meaningful conclusion.",
            "short": "Include a clear beginning, one or two complications, and a resolution. Focus on a single plotline.",
            "medium": "Develop a main plot with 1-2 smaller subplots. Structure with clear introduction, rising action, climax and resolution.",
            "long": "Balance multiple plot elements with a strong central arc. Include deeper character development and more complex narrative structure."
        }
        
        return guidance.get(length, "")

    def _get_length_character_guidance(self, length: str) -> str:
        """Get character development guidance specific to story length."""
        guidance = {
            "micro": "Limit to 1-2 characters, revealed through specific actions or details rather than description.",
            "short": "Focus on 2-3 key characters with one primary trait each, revealed through action and dialogue.",
            "medium": "Develop 3-5 characters with multiple traits and motivations. Include character arcs for main characters.",
            "long": "Create deeper character backgrounds, internal conflicts, and evolving relationships. Support main characters with secondary characters."
        }
        
        return guidance.get(length, "")

    def _get_length_pacing_guidance(self, length: str) -> str:
        """Get pacing guidance specific to story length."""
        guidance = {
            "micro": "Every word must serve the story. Use rapid pacing with immediate narrative hooks and tight conclusion.",
            "short": "Quick introduction, limited exposition, and efficient movement to the main conflict and resolution.",
            "medium": "Balance action with reflection. Include 2-3 key plot developments before the climax.",
            "long": "Vary pacing throughout, with multiple rises and falls in tension. Include moments of action, reflection, character development, and world building."
        }
        
        return guidance.get(length, "")

    def get_story_length_options(self) -> Dict[str, Dict[str, Any]]:
        """Return all story length options with their details."""
        return self.STORY_LENGTHS

    def process(self, request: ToolRequest, context: Dict[str, Any]) -> ToolResponse:
        """Process a tool request and return a tool response."""
        message = request.input
        user_id = request.user_id
        
        logger.info(f"Processing story request from {user_id}: {message}")
        
        # Check if this is coming from the story create endpoint
        is_direct_creation = context.get("direct_creation", False)
        
        # Only check for creation redirect if NOT coming from the story create endpoint
        if not is_direct_creation and self._is_story_creation_request(message):
            logger.info("Story creation request detected - redirecting to StoryCreator")
            # Return a special signal for redirection
            return ToolResponse(
                output="Let's create a story! Taking you to the story creator...",
                success=True,
                data=json.dumps({"redirect": "StoryCreator"})
            )
        
        # Extract story parameters
        params = self._extract_story_parameters(message, context)
        
        # Generate the story using parameters from context first, then extracted params
        genre = context.get("genre") or params.get("genre") or "fantasy"
        mood = context.get("mood") or params.get("mood") or "mysterious" 
        length = context.get("length") or params.get("length") or "short"
        
        logger.info(f"Generating {length} {mood} {genre} story for {user_id}")
        
        story = self._generate_story(genre, mood, length, user_id)
        
        # Create response data
        data_dict = {"genre": genre, "mood": mood, "length": length}
        
        return ToolResponse(
            output=story,
            success=True,
            data=json.dumps(data_dict)
        )

    def _is_story_creation_request(self, message: str) -> bool:
        """Determine if the message is requesting story creation."""
        # Use regex patterns to identify story creation requests
        creation_patterns = [
            r"\b(?:create|write|make|generate|start|build|develop)\b.*?\b(?:story|tale|narrative)\b",
            r"\b(?:story\s*?creator|story\s*?creation)\b",
            r"\b(?:new|another)\s+(?:story|tale)\b", 
            r"(?:^|\s)story(?:$|\s)",      # Just the word "story" by itself
            r"(?:^|\s)write(?:$|\s)",      # Just the word "write" by itself
            r"(?:^|\s)create(?:$|\s)",     # Just the word "create" by itself
            r"\b(?:ready|prepared|want|like) to (?:write|create|make)\b",
            r"\bi (?:want|would like) (?:a|to write|to create)\b.*?\b(?:story|tale)\b"
        ]
        
        message_lower = message.lower()
        
        # Check against each pattern
        for pattern in creation_patterns:
            if re.search(pattern, message_lower):
                return True
            
        # Also check for explicit story keywords if they make up most of the message
        story_keywords = ["story", "write", "create", "tale", "narrative"]
        word_count = len(message_lower.split())
        
        # If the message is short (1-3 words) and contains a story keyword
        if word_count <= 3:
            for keyword in story_keywords:
                if keyword in message_lower:
                    return True
        
        return False
    
    def generate_story(self, user_id: str, genre: str, mood: str, length: str, 
                      characters: list = None, plot_elements: list = None) -> str:
        """
        Directly generate a story based on UI parameters.
        This method is called by the /api/story/create endpoint.
        """
        logger.info(f"Generating {length} {mood} {genre} story for {user_id}")
        
        characters = characters or []
        plot_elements = plot_elements or []
        
        # Use the existing _generate_story method
        return self._generate_story(
            genre=genre,
            mood=mood,
            length=length,
            characters=characters,
            plot_elements=plot_elements,
            user_id=user_id
        )