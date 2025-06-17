import logging
from typing import Dict, Callable, Any, List, Optional
from pydantic import PrivateAttr

from ..models.schemas import ToolRequest, ToolResponse
from google.adk.agents import LlmAgent
from . import client
from multi_tool_agent.config.response import FAQ_RESPONSES, STORY_TEMPLATES, ERROR_MESSAGES
import google.generativeai as genai

logger = logging.getLogger(__name__)

class FAQAgent(LlmAgent):
    """
    A specialized agent that handles frequently asked questions and commands
    based on predefined keyword patterns and static responses.
    It first attempts to match user queries to predefined FAQ patterns.
    If no direct match is found, it uses a generative AI model to provide a response.
    """

    # Use PrivateAttr for internal attributes that are not part of the Pydantic model's public API
    _faq_patterns: Dict[str, Dict[str, Any]] = PrivateAttr()
    _story_intent_keywords: List[str] = PrivateAttr()
    _genre_keywords: List[str] = PrivateAttr()

    def __init__(self, model_name: str = "gemini-1.5-flash"):
        """
        Initializes the FAQAgent with a specified LLM model and pre-defined FAQ patterns.

        Args:
            model_name (str): The name of the generative model to use for AI responses.
        """
        super().__init__(
            model=model_name,
            name="faq_agent",
            description="Answers common questions and provides guidance on using PlotBuddy.",
            instruction="You are a helpful FAQ assistant. Your task is to provide predefined answers to common questions or leverage AI to respond."
        )
        # Define more comprehensive patterns with broader keyword matches
        self._faq_patterns = {
            "help": {
                "keywords": ["help", "instructions", "guide", "commands", "how to use", "options", "features"],
                "response_key": "HELP_MESSAGE"
            },
            "genre": {
                "keywords": ["genre", "genres", "what genres", "story types", "types of stories", 
                            "story genres", "available genres", "kind of stories", "what stories"],
                "response_key": "GENRES_MESSAGE"
            },
            "pricing": {
                "keywords": ["price", "prices", "pricing", "cost", "how much", "payment", 
                            "subscription", "plan", "fee", "charge", "money", "dollar"],
                "response_key": "PRICING_MESSAGE"
            },
            "contact": {
                "keywords": ["contact", "support", "email", "phone", "reach out", "support team", 
                            "help desk", "customer service", "tech support"],
                "response_key": "CONTACT_MESSAGE"
            },
            "hours": {
                "keywords": ["hour", "hours", "business hours", "open", "when", "availability",
                            "support hours", "operating hours", "available time", "schedule"],
                "response_key": "HOURS_MESSAGE"
            },
            "how_it_works": {
                "keywords": ["how it works", "how does it work", "process", "explain", "details", 
                            "steps", "guide me", "tutorial", "instructions", "workflow"],
                "response_key": "HOW_IT_WORKS_MESSAGE"
            }
        }

        # Keywords for detecting story creation intent
        self._story_intent_keywords = [
            "let's start", "i'm ready", "create story", "write story", "make story",
            "start writing", "begin story", "let's write", "ok", "okay", "sure",
            "let's do it", "sounds good", "ready", "i want to try", "i am ready",
            "redy", "im ready", "i think i am ready", "i think im ready", "good to go",
            "start a story", "begin a story", "write me a story",
            
            # Add new keywords for examples
            "example", "sample", "show me", "give me an example", "give me a sample", 
            "can you show", "can i see", "give me the example", "show example",
            "demo", "try it", "try out", "let's try", "let me try"
        ]

        # Keywords for specific genre selection (indicating story creation intent)
        self._genre_keywords = [
            "fiction", "fantasy", "sci-fi", "science fiction", "mystery", "thriller",
            "horror", "romance", "adventure", "historical", "western", 
            "comedy", "drama", "novel", "story about", "cyberpunk"
        ]

        logger.info("FAQAgent initialized.")

    def process(self, request: ToolRequest) -> ToolResponse:
        """Handles incoming tool requests for FAQ queries."""
        logger.debug(f"FAQAgent processing request for user {request.user_id} with input: {request.input}")

        # Add more detailed logging
        logger.info(f"⏺️ FAQ AGENT RECEIVED: '{request.input}'")

        if not isinstance(request.input, str):
            logger.warning(f"FAQAgent received non-string input: {type(request.input)}. Returning fallback message.")
            return ToolResponse.error(ERROR_MESSAGES["INVALID_INPUT_TYPE"])

        message_lower = request.input.lower().strip()
        
        # IMPORTANT: Check for genre keywords FIRST, before other patterns
        # Move this block above your other pattern checks
        if any(genre.lower() in message_lower for genre in self._genre_keywords):
            detected_genre = next((genre for genre in self._genre_keywords if genre.lower() in message_lower), "that")
            logger.info(f"Genre keyword detected: '{message_lower}'")
            
            # Make sure to include the FORCE redirect flag
            return ToolResponse(
                success=True,
                output=f"Great! Let's create a story in the {detected_genre} genre. Taking you to the story creator now.",
                message="REDIRECT_TO_STORY_CREATOR_FORCE"  # Critical for redirection
            )
        
        
        # Check direct FAQ patterns with debug logging
        for category, pattern in self._faq_patterns.items():
            keywords_found = [kw for kw in pattern["keywords"] if kw in message_lower]
            if keywords_found:
                logger.info(f"✅ FAQ pattern matched: {category} for '{message_lower}', keywords: {keywords_found}")
                return ToolResponse(
                    success=True,
                    output=FAQ_RESPONSES[pattern["response_key"]]
                )
            else:
                logger.debug(f"No match for {category}: none of {pattern['keywords']} found in '{message_lower}'")
    
        # If no pattern matched, log the failure
        logger.info(f"❌ No FAQ pattern matched for: '{message_lower}'")

        # --- Story Creation Intent Detection ---
        # Check for direct story creation intents FIRST
        if any(keyword in message_lower for keyword in self._story_intent_keywords):
            logger.info(f"Story intent keyword detected: '{message_lower}'")
            
            # Check context for previous redirect attempts
            context = request.context or {}
            redirect_attempts = context.get("redirect_attempts", 0)
            
            if redirect_attempts > 0:
                # If already attempted to redirect, give a more direct message
                return ToolResponse(
                    success=True,
                    output="I'm taking you to the story creator now! You'll be able to select your genre, mood, and length there.",
                    message="REDIRECT_TO_STORY_CREATOR_FORCE"  # Special flag for forced redirect
                )
            else:
                # First redirect attempt
                # Update context to track that we've tried to redirect once
                new_context = dict(context)
                new_context["redirect_attempts"] = 1
                request.context = new_context
                
                return ToolResponse(
                    success=True,
                    output="Great! Let's create your story.",
                    message="REDIRECT_TO_STORY_CREATOR"  # Standard redirect flag
                )
        
        # (Removed redundant genre keyword check block; genre intent is already handled above.)
        
        # --- Generative AI Fallback for Unmatched Queries ---
        try:
            if client.GOOGLE_API_KEY:
                # Craft a dynamic prompt for the generative AI
                prompt = self._construct_ai_prompt(request.input)
                model = genai.GenerativeModel(self.model) # Use the model specified in __init__
                
                # Configure generation to be more concise and direct
                generation_config = genai.GenerationConfig(
                    temperature=0.4,  # Slightly lower temperature for more focused answers
                    max_output_tokens=150, # Limit output length
                )

                response = model.generate_content(prompt, generation_config=generation_config)

                if hasattr(response, 'text') and response.text:
                    ai_response = response.text.strip()
                    logger.info(f"FAQAgent generated AI response for '{request.input}': {ai_response}")
                    return ToolResponse(success=True, output=ai_response)
                else:
                    logger.warning(f"AI response for '{request.input}' was empty or malformed.")
            else:
                logger.warning("No Google API key available for AI response generation. Falling back to default message.")

        except Exception as e:
            logger.error(f"Error generating AI FAQ response for '{request.input}': {e}")
            # Optionally, log the full traceback for debugging: logger.exception("Error generating AI response")

        # --- Final Fallback ---
        logger.info(f"FAQAgent could not match or generate AI response for query '{request.input}'. Returning fallback message.")
        return ToolResponse(success=True, output=FAQ_RESPONSES["DEFAULT_FALLBACK"], message=None)

    def _construct_ai_prompt(self, user_query: str) -> str:
        """Constructs the prompt for the generative AI model."""
        return f"""You are PlotBuddy, a helpful and friendly AI storytelling assistant.
Your main goal is to assist users with common questions about PlotBuddy or guide them towards creating stories.

Based on the following user query, provide a concise and direct answer.

Here is the user's query: "{user_query}"

IMPORTANT RULES:
- Be conversational and directly address the user.
- Do NOT explicitly mention "AI", "model", or "I am an AI".
- Do NOT ask follow-up questions unless absolutely necessary.
- Keep your response under 100 words.
- Avoid starting every response with greetings like "Hey there!", "Hi!", "Hello", etc.
- Only use a greeting in the very first message of a conversation, not in follow-up responses.
- If the query mentions "support", "contact", "login issues", "account" or any request to speak with someone, ALWAYS respond with contact information.
- For support and contact requests, direct them to email support@plotbuddy.ai or visit help.plotbuddy.ai
- If the query is about a feature PlotBuddy does not have, gently explain that feature is not available and suggest alternatives.

Now, respond to the user's query:
"""

# --- Static Responses (Moved to multi_tool_agent.config.response.py or similar) ---
# For demonstration purposes, including them here as a dictionary.
# In a real application, these would be loaded from a configuration file or a separate module.

# Simulate content from multi_tool_agent.config.response
# You would actually import GREETING_RESPONSES, FAQ_RESPONSES, etc., from your config file.
# For the purpose of this improved code, I'm defining FAQ_RESPONSES directly.

# Please ensure 'multi_tool_agent.config.response' is updated accordingly.
# For this example, I'm defining the FAQ_RESPONSES here to make the code runnable independently.
# In your actual project, `FAQ_RESPONSES` should be imported from `multi_tool_agent.config.response`.

# Example structure of multi_tool_agent.config.response.py
# FAQ_RESPONSES = { ... }
# STORY_TEMPLATES = { ... }
# ERROR_MESSAGES = { ... }
# GREETING_RESPONSES = { ... }

# TEMPORARY: Define FAQ_RESPONSES here for immediate testing.
# In a real application, ensure these are loaded from your config.
FAQ_RESPONSES = {
    "HELP_MESSAGE": (
        "🚀 **Welcome to PlotBuddy Help!**\n\n"
        "Here's how I can help you today:\n"
        "--- **General Commands** ---\n"
        "  • Type `help` to see this message again.\n"
        "  • Ask `how it works` to understand my creative process.\n"
        "  • Say `contact support` for help or feedback.\n\n"
        "--- **Story Creation** ---\n"
        "  • Ask `what genres` are available to get inspired.\n"
        "  • To start a story, tell me `create story` or `write a story` (then specify genre, mood, and length!).\n\n"
        "--- **Account & Pricing** ---\n"
        "  • Ask `what are your prices` or `subscription plans`.\n"
        "  • Query `business hours` for support availability.\n\n"
        "**💡 Tip:** Try being specific! For example: 'Create a short sci-fi story with a mysterious mood.'\n"
        "I'm here to bring your ideas to life!"
    ),
    "PRICING_MESSAGE": (
        "💰 **PlotBuddy Pricing & Plans** 💰\n\n"
        "--- **Individual Story Packs** ---\n"
        "  • **1 Story Credit:** $4.99\n"
        "  • **5 Story Credits:** $19.99 (Save 20%)\n"
        "  • **10 Story Credits:** $34.99 (Save 30%)\n\n"
        "--- **Subscription Tiers (Best Value!)** ---\n"
        "  • **Bronze (5 stories/month):** $17.99/month\n"
        "  • **Silver (20 stories/quarter):** $67.99/quarter (equivalent to ~$16.99/month)\n"
        "  • **Gold (100 stories/year):** $199.99/year (equivalent to ~$16.67/month)\n\n"
        "All subscriptions include priority support and early access to new features!\n"
        "Ready to start your storytelling journey? Just ask for 'help' if you have more questions!"
    ),
    "GENRES_MESSAGE": (
        "📚 **Available Story Genres** 📚\n\n"
        "I can craft tales in a wide array of genres, including:\n"
        "  • **Adventure:** Thrilling quests and daring escapades.\n"
        "  • **Comedy:** Lighthearted and humorous narratives.\n"
        "  • **Cyberpunk:** Dystopian futures with advanced tech and low-life.\n"
        "  • **Fantasy:** Magic, mythical creatures, and fantastical worlds.\n"
        "  • **Historical:** Stories set in the past, blending fact and fiction.\n"
        "  • **Horror:** Spine-chilling and suspenseful tales.\n"
        "  • **Mystery:** Puzzles, clues, and secrets to unravel.\n"
        "  • **Romance:** Stories of love and relationships.\n"
        "  • **Sci-Fi:** Futuristic concepts, technology, and space exploration.\n"
        "  • **Thriller:** High suspense, tension, and unexpected twists.\n"
        "  • **Western:** Tales of the American Old West.\n\n"
        "**Popular Genre Combinations:**\n"
        "  • **Sci-Fi Mystery:** Solve crimes in a futuristic world\n"
        "  • **Fantasy Adventure:** Epic quests in magical realms\n"
        "  • **Historical Romance:** Love stories set in fascinating time periods\n"
        "  • **Horror Comedy:** Scary situations with humorous twists\n"
        "  • **Western Fantasy:** Magic in the old frontier\n\n"
        "What kind of story would you like me to create for you today?"
    ),
    "GENRE_SUGGESTIONS_MESSAGE": (
        "🌟 **Need Genre Inspiration?** 🌟\n\n"
        "Not sure what to write? Here are some fantastic options to spark your imagination:\n\n"
        "**For beginners:**\n"
        "• **Adventure:** Action-packed journeys with brave heroes\n"
        "• **Mystery:** Solve an intriguing puzzle or crime\n"
        "• **Fantasy:** Magical worlds with unlimited possibilities\n\n"
        "**Exciting combinations to try:**\n"
        "• **Sci-Fi Mystery:** A detective story on a space station\n"
        "• **Historical Fantasy:** Magic in a real historical setting\n"
        "• **Romantic Comedy:** Love story with humor and heart\n\n"
        "**Just tell me:**\n"
        "\"Create a [genre] story with a [mood] mood\"\n"
        "For example: \"Create a mystery story with a suspenseful mood\"\n\n"
        "What sounds most interesting to you? I'm here to help bring your story to life!"
    ),
    "HOW_IT_WORKS_MESSAGE": (
        "✨ **How PlotBuddy Works: Your Story Creation Journey** ✨\n\n"
        "It's super simple to bring your ideas to life:\n"
        "1.  **Tell me what you want:** Start by saying 'create story' or 'write me a story'.\n"
        "2.  **Define your story:** I'll then ask you for three key things:\n"
        "    - **Genre:** (e.g., fantasy, sci-fi, mystery)\n"
        "    - **Mood:** (e.g., mysterious, whimsical, dark)\n"
        "    - **Length:** (e.g., micro, short, medium, long)\n"
        "    *Example: 'Write a short sci-fi story with a tense mood.'*\n"
        "3.  **Generate!** I'll get to work crafting a unique narrative just for you.\n"
        "4.  **Review & Refine:** Read your story! You can then save it or generate another.\n\n"
        "Let's get writing!"
    ),
    "HOURS_MESSAGE": "🕒 **PlotBuddy Support Hours:**\nOur dedicated support team is available from **9 AM to 9 PM PDT**, seven days a week. We're here to help you anytime!",
    "CONTACT_MESSAGE": (
        "📞 **Need to Reach Us?**\n\n"
        "For support, feedback, or inquiries, you can:\n"
        "  • **Email Us:** support@plotbuddy.ai\n"
        "  • **Visit Our Help Center:** help.plotbuddy.ai (coming soon!)\n"
        "  • Our team is available 9 AM - 9 PM PDT, 7 days a week."
    ),
    "DEFAULT_FALLBACK": (
        "🤔 **Hmm, I'm not quite sure what you're asking.**\n"
        "Could you please rephrase your question, or try one of these common commands?\n\n"
        "  • `help` - To see a list of all commands.\n"
        "  • `how it works` - To learn about story creation.\n"
        "  • `what genres` - To explore available story types.\n"
        "  • `pricing` - To find out about costs and subscriptions.\n\n"
        "I'm here to help you write awesome stories!"
    ),
    "REDIRECT_TO_STORY_CREATOR_MESSAGE": "Great! I'll take you to the story creator now. You can choose your genre, mood, and length to get started."
}

# Assume ERROR_MESSAGES is also defined in multi_tool_agent.config.response
ERROR_MESSAGES = {
    "INVALID_INPUT_TYPE": "Please provide your query as text. Type 'help' for options."
}

# For testing (ensure these match your actual schema definitions or mock them appropriately)
if __name__ == "__main__":
    from pydantic import BaseModel

    # Mocking ToolRequest and ToolResponse for standalone testing
    class MockToolRequest(BaseModel):
        user_id: str
        input: Any
        context: Optional[Dict[str, Any]] = None

    class MockToolResponse(BaseModel):
        success: bool = True
        output: Optional[str] = None
        message: Optional[str] = None # Added message to match the class definition

        @classmethod
        def error(cls, msg: str) -> "MockToolResponse":
            return cls(success=False, output=msg, message="ERROR") # Use output for the message

        @classmethod
        def success(cls, data: str, message: Optional[str] = None) -> "MockToolResponse":
            return cls(success=True, output=data, message=message)

    # Overriding the imported ToolRequest and ToolResponse for testing scope
    ToolRequest = MockToolRequest
    ToolResponse = MockToolResponse

    # Mock the client.GOOGLE_API_KEY for testing purposes
    class MockClient:
        GOOGLE_API_KEY = "MOCKED_API_KEY" # Set to a non-empty string to enable AI path
    client = MockClient()

    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    agent = FAQAgent()
    test_queries = [
        "help me",
        "what are the prices?",
        "tell me about genres",
        "how does this work?",
        "what are your business hours?",
        "I need support",
        "random question about cats", # Should go to AI
        "create story", # Should trigger story intent
        "write a fantasy story", # Should trigger genre-specific story intent
        "I am ready to write", # Should trigger story intent
        "suggest a genre for me", # Should trigger genre suggestions
        123, # Non-string input
        "tell me about plotbuddy", # Should go to AI
        "what's a good mood for a horror story?", # Should go to AI
        "what kind of stories can you write?" # Should hit genres
    ]

    print("--- Testing FAQAgent ---")
    for query in test_queries:
        print(f"\nQ: {query}")
        response = agent.process(ToolRequest(user_id="test_user", input=query))
        print(f"A: {response.output}\n   (Message: {response.message})") # Print both output and message
        print("-" * 50)