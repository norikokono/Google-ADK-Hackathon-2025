import logging
from typing import Dict, Callable, Any, List, Optional
from pydantic import PrivateAttr
import re

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
            },
            "using_plotbuddy": {
                "keywords": ["how to use plotbuddy", "using plotbuddy", "plotbuddy guide", "navigating plotbuddy"],
                "response_key": "USING_PLOTBUDDY_MESSAGE"
            }
        }

        # Keywords for detecting story creation intent
        self._story_intent_keywords = [
            "let's start", "i'm ready", "create story", "write story", "make story",
            "start writing", "begin story", "let's write", "write a story", "generate story",
            "new story", "story idea", "plot", "narrative", "story prompt", "story generation",
            "story creation", "story writing", "story prompt", "story concept", "create a story",
            "write a plot", "write a narrative", "write a story idea", "write a story prompt",
            "write a story concept", "i want to create a story", "i want to write a story",
            "i want to generate a story", "i want to make a story", "i want to start a story",
            "i want to write", "i want to create", "i want to generate", "i want to make",
            "i want to begin", "i want to start", "i want to write a plot", "i want to write a narrative",
            "i want to write a story idea", "i want to write a story prompt", "i want to write a story concept",
            "let's create a story", "let's write a story", "let's generate a story", "let's make a story",
            "let's start a story", "let's write a plot", "let's write a narrative",
            "let's do it","ready", "i want to try", "i am ready", "redy", "im ready", "i think i am ready", "i think im ready", 
            "good to go", "start a story", "begin a story", "write me a story",
            
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
        """Process an FAQ request with intelligent intent detection."""
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
    to assist users with common questions about PlotBuddy or guide them towards creating stories.

    You're a polite, empathetic, and knowledgeable assistant.
    Greet customers warmly and address them directly.
    Listen carefully, ask clarifying questions when needed, and validate their concerns.
    Use clear, simple language and avoid overly technical terms.
    If an issue is complex, explain the next steps clearly.
    Always summarize your solutions and invite follow-up questions to ensure complete satisfaction.
    Make sure to provide concise and direct answers and avoid unnecessary repetition.

    Based on the following user query, provide a concise and direct answer.

    Here is the user's query: "{user_query}"

    IMPORTANT RULES:
    - Be conversational and directly address the user.
    - Do NOT explicitly mention "AI", "model", or "I am an AI".
    - Keep your response under 100 words.
    - IMPORTANT: Avoid starting every response with greetings like "Hey there!", "Hi!", "Hello", etc.
    - IMPORTANT: Only use a greeting in the very first message of a conversation, not in follow-up responses.
    - If the query mentions "support", "contact", "login issues", "account" or any request to speak with someone, ALWAYS respond with contact information.
    - For support and contact requests, direct them to email support@plotbuddy.ai or visit help.plotbuddy.ai
    - If the query is about a feature PlotBuddy does not have, gently explain that feature is not available and suggest alternatives.

    Now, respond to the user's query:
    """

    # Update the FAQ agent's pattern matching in faq.py
    def _is_faq_question(self, message: str) -> bool:
        """Determine if a message is an FAQ question."""
        # Add more robust application-specific keywords
        app_keywords = [
            r"\b(?:plotbuddy|plot buddy|app|application|tool|platform|website|site)\b",
            r"\b(?:how to use|using|work with|navigate|access|feature|function)\b",
            r"\b(?:account|profile|settings|preferences|login|signup|register)\b",
            r"\b(?:save|export|import|share|download|upload)\b",
        ]
        
        # Check for application keywords combined with question patterns
        question_patterns = [
            r"\b(?:how do I|how to|how can I|what is|can I|does|is there|where is)\b",
            r"\b(?:help|question|faq|guide|tutorial|documentation|support)\b",
            r"\?$"  # Ends with question mark
        ]
        
        # First check: if mentions our app name directly with a question, it's almost certainly FAQ
        for app_term in [r"\b(?:plotbuddy|plot buddy)\b"]:
            if re.search(app_term, message.lower()):
                for q_pattern in question_patterns:
                    if re.search(q_pattern, message.lower()):
                        return True
        
        # Second check: other app-related terms with questions
        for app_term in app_keywords:
            if re.search(app_term, message.lower()):
                for q_pattern in question_patterns:
                    if re.search(q_pattern, message.lower()):
                        return True
        
        return False

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
        "Here's what I can help you with:\n"
        "— **General Commands:**\n"
        "  • Type `help` to see this menu again.\n"
        "  • Ask `how it works` for a quick overview.\n"
        "  • Say `contact support` for assistance or feedback.\n\n"
        "— **Story Creation:**\n"
        "  • Ask `what genres` to explore story types.\n"
        "  • To start, just say `create story` or `write a story` (then pick genre, mood, and length!).\n\n"
        "— **Account & Pricing:**\n"
        "  • Ask about `pricing` or `subscription plans`.\n"
        "  • Query `business hours` for support times.\n\n"
        "**💡 Tip:** Be specific! For example: 'Create a short sci-fi story with a mysterious mood.'\n"
        "I'm here to help you bring your ideas to life!"
    ),
    "PRICING_MESSAGE": (
        "💰 **PlotBuddy Pricing & Plans** 💰\n\n"
        "**Story Credits:**\n"
        "  • 1 Credit: $4.99\n"
        "  • 5 Credits: $19.99 (Save 20%)\n"
        "  • 10 Credits: $34.99 (Save 30%)\n\n"
        "**Subscriptions (Best Value!):**\n"
        "  • Bronze (5/month): $17.99/mo\n"
        "  • Silver (20/quarter): $67.99/quarter (~$16.99/mo)\n"
        "  • Gold (100/year): $199.99/year (~$16.67/mo)\n\n"
        "All plans include priority support and early feature access!\n"
        "Questions? Just ask for 'help'."
    ),
    "GENRES_MESSAGE": (
        "📚 **Available Story Genres** 📚\n\n"
        "I can write stories in many genres, including:\n"
        "  • Adventure\n"
        "  • Comedy\n"
        "  • Cyberpunk\n"
        "  • Fantasy\n"
        "  • Historical\n"
        "  • Horror\n"
        "  • Mystery\n"
        "  • Romance\n"
        "  • Sci-Fi\n"
        "  • Thriller\n"
        "  • Western\n\n"
        "**Popular combos:**\n"
        "  • Sci-Fi Mystery\n"
        "  • Fantasy Adventure\n"
        "  • Historical Romance\n"
        "  • Horror Comedy\n"
        "  • Western Fantasy\n\n"
        "What kind of story would you like to create?"
    ),
    "GENRE_SUGGESTIONS_MESSAGE": (
        "🌟 **Need Genre Inspiration?** 🌟\n\n"
        "Not sure what to write? Try these:\n"
        "• Adventure: Action-packed journeys\n"
        "• Mystery: Solve a puzzle or crime\n"
        "• Fantasy: Magical worlds\n\n"
        "Or mix it up:\n"
        "• Sci-Fi Mystery: Detective in space\n"
        "• Historical Fantasy: Magic in real history\n"
        "• Romantic Comedy: Love with humor\n\n"
        "Just say: \"Create a [genre] story with a [mood] mood\"\n"
        "What sounds fun to you?"
    ),
    "HOW_IT_WORKS_MESSAGE": (
        "✨ **How PlotBuddy Works** ✨\n\n"
        "1. I'll ask for genre, mood, and length.\n"
        "2. I'll generate your story!\n"
        "3. Read, save, or create another.\n\n"
        "Ready to get started?"
    ),
    "HOURS_MESSAGE": (
        "🕒 **Support Hours:**\n"
        "Our team is available 9 AM – 9 PM PDT, 7 days a week."
    ),
    "CONTACT_MESSAGE": (
        "📞 **Contact Us:**\n"
        "• Email: support@plotbuddy.ai\n"
        "• Help Center: help.plotbuddy.ai (coming soon!)\n"
        "We're here 9 AM – 9 PM PDT, every day."
    ),
    "PROFILE_OVERVIEW": (
        "👤 **Your PlotBuddy Profile**\n\n"
        "View your subscription, story credits, and recent activity here. "
        "Want to update preferences or see your story history? Just ask!"
    ),
    "PROFILE_UPDATE_SUCCESS": (
        "✅ **Profile Updated!**\n\n"
        "Your preferences are saved. Need to change anything else?"
    ),
    "PROFILE_UPDATE_FAIL": (
        "⚠️ **Profile Update Failed**\n\n"
        "Sorry, I couldn't update your profile. Please try again or contact support."
    ),
    "PROFILE_CREDITS": (
        "💎 **Story Credits**\n\n"
        "You have {credits} story credits left. "
        "Need more? Ask about pricing or plans!"
    ),
    "DEFAULT_FALLBACK": (
        "🤔 **I didn't quite get that.**\n\n"
        "Try one of these:\n"
        "• Type `help` for options\n"
        "• Ask me to `create story` or `write a [genre] story`\n"
        "• Try `what genres` or `suggest a genre for me`\n"
        "• Ask about `pricing` or `subscription plans`\n"
        "• Say `how it works` for a quick guide\n"
        "• Need help? Type `contact support`\n\n"
        "✨ The more details you give, the better I can help!"
    ),
    "REDIRECT_TO_STORY_CREATOR_MESSAGE": (
        "Great! I'll take you to the story creator now. You can choose your genre, mood, and length to get started."
    ),
    "USING_PLOTBUDDY_MESSAGE": (
        "# Using PlotBuddy - Quick Start\n\n"
        "1. **Home:** Start here for help\n"
        "2. **Story Creator:** Begin a new story\n"
        "3. **Plot Generator:** Get inspiration\n\n"
        "To create your first story:\n"
        "1. Click \"Create Story\"\n"
        "2. Choose length, genre, and mood\n"
        "3. Save your story\n\n"
        "Type \"help\" anytime for assistance!"
    )
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