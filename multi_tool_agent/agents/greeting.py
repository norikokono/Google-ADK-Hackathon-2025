import logging
logger = logging.getLogger(__name__) # Moved this line to the very top

import os
from datetime import datetime
from typing import ClassVar, Set, Any, Dict, Optional
import json

# Local module imports
from ..models.schemas import ToolRequest, ToolResponse

# Third-party imports
from google.adk.agents import LlmAgent
import google.generativeai as genai

# Import from your 'llms' directory
try:
    from . import client
    logger.debug("Successfully imported llms client utilities.")
except ImportError:
    logger.warning("Could not import llms client utilities. Ensure multi_tool_agent/llms/client.py exists if intended.")
    client = None # Ensure client is None if import fails

# Assuming these are properly defined in your config
from multi_tool_agent.config.response import GREETING_RESPONSES, FAQ_RESPONSES, STORY_TEMPLATES, ERROR_MESSAGES


class GreetingAgent(LlmAgent):
    """
    An agent that handles user greetings, provides a warm welcome,
    and can identify an immediate intent to create a story.
    """

    # Class variables for common greetings and story creation keywords
    greetings: ClassVar[Set[str]] = {
        "hello", "hi", "hey", "greetings",
        "good morning", "good afternoon", "good evening",
        "howdy", "hola", "welcome", "plotbuddy", "plot buddy",
        "start", "let's start" # Added "start" for general initiation
    }

    story_creation_keywords: ClassVar[Set[str]] = {
        "create story", "write story", "make story",
        "start writing", "begin story", "let's write", "ready to write",
        "compose story", "tell me a story", "story" # Added 'story' for a broader match
    }

    def __init__(self, model_name: str = "gemini-1.5-flash"):
        """
        Initializes the GreetingAgent.

        Args:
            model_name (str): The name of the generative model to use for personalized greetings.
        """
        super().__init__(
            model=model_name,
            name="greeting_agent",
            description="Welcomes users, offers initial guidance, and can identify story creation intent.",
            instruction="You are a friendly AI assistant that greets users warmly and encourages story creation."
        )
        logger.info("GreetingAgent initialized.")

    def process(self, request: ToolRequest, context: Dict[str, Any] = None) -> ToolResponse:
        """Process the greeting request"""
        # Initialize context if None
        if context is None:
            context = {}
            
        user_id = request.user_id
        message = request.input  # Changed from request.message
        
        # Check if this is a greeting or non-greeting query
        message_lower = message.lower().strip()
        
        # Define greeting-specific keywords
        greeting_keywords = ["hi", "hello", "hey", "howdy", "greetings", "good morning", 
                            "good afternoon", "good evening", "hola", "welcome", "yo", "sup"]
        
        # Define clear NON-greeting keywords that should be handled by other agents
        faq_keywords = ["what", "how", "who", "when", "where", "why", "tell me about", 
                        "explain", "help", "genres", "pricing", "price", "prices", "cost", 
                        "subscription", "hour", "contact", "support"]
        
        # If the message contains FAQ keywords or doesn't contain any greeting keywords,
        # this is NOT a greeting and should be handled by another agent
        if any(keyword in message_lower for keyword in faq_keywords):
            logger.info(f"FAQ content detected in: '{message}' - declining to process")
            return ToolResponse(success=False, message="Not a greeting message")
        
        if not any(word in message_lower for word in greeting_keywords):
            logger.info(f"No greeting keywords found in: '{message}' - declining to process")
            return ToolResponse(success=False, message="Not a greeting message")
            
        # Otherwise, proceed with normal greeting processing
        # Determine time of day for fallback greeting
        hour = datetime.now().hour # Use current local hour
        if 5 <= hour < 12:
            time_of_day = "morning"
            fallback_response = GREETING_RESPONSES.get("morning", "Good morning!")
        elif 12 <= hour < 18:
            time_of_day = "afternoon"
            fallback_response = GREETING_RESPONSES.get("afternoon", "Good afternoon!")
        else:
            time_of_day = "evening"
            fallback_response = GREETING_RESPONSES.get("evening", "Good evening!")

        # Try to use LLM for personalized greeting
        try:
            if client and hasattr(client, 'GOOGLE_API_KEY') and client.GOOGLE_API_KEY:
                # Ensure the API key is configured if not already global
                genai.configure(api_key=client.GOOGLE_API_KEY)

                model = genai.GenerativeModel(self.model)

                # Create personalized greeting prompt
                # Improved prompt for more reliable LLM responses
                prompt = f"""The user greeted you with: "{message}"

You are PlotBuddy, a friendly and enthusiastic AI creative writing assistant.

CRITICAL INSTRUCTIONS:
- NEVER begin responses with phrases like "As an AI..." or "The user is asking..."
- NEVER include your reasoning, analysis, or thought process
- Respond directly as PlotBuddy in a warm, casual tone
- Mention that it's currently {time_of_day} (e.g., "Good morning!")
- Briefly mention that you help with creating stories
- Include 1-2 relevant emojis
- Keep your response VERY short - maximum 2 sentences
- Do NOT ask questions like "How can I assist you today?" or "What would you like to do?".
- Do NOT explicitly mention "AI", "model", or "I am an AI".
- Gently invite them to create a story or ask for help, without directly asking a question.

Now, craft your personalized greeting:
"""

                # Generate greeting with a low temperature for consistent, direct responses
                generation_config = genai.GenerationConfig(
                    temperature=0.7, # A bit of creativity, but still focused
                    max_output_tokens=70 # Ensure conciseness
                )
                logger.info(f"Generating LLM greeting for input: '{message}' with time of day: {time_of_day}")
                genai_response = model.generate_content(prompt, generation_config=generation_config)

                if hasattr(genai_response, 'text') and genai_response.text.strip():
                    llm_greeting = genai_response.text.strip()
                    logger.info(f"Successfully generated personalized greeting with LLM: '{llm_greeting}'")
                    return ToolResponse(success=True, output=llm_greeting)
                else:
                    logger.warning("LLM returned empty or malformed response, using fallback greeting.")
            else:
                logger.warning("Google API key not available for LLM greeting. Using fallback greeting.")

        except Exception as e:
            logger.error(f"Error generating personalized greeting with LLM: {e}")
            # Log full traceback for debugging
            logger.exception("Details of LLM greeting error:")

        # Fall back to template response if LLM fails or is not available
        logger.info(f"Using template greeting as fallback for '{message}'.")
        return ToolResponse(success=True, output=fallback_response)


# --- For local testing purposes ---
if __name__ == "__main__":
    from pydantic import BaseModel

    # Mock ToolRequest and ToolResponse for standalone testing
    class MockToolRequest(BaseModel):
        user_id: str
        input: Any
        context: Optional[Dict[str, Any]] = None

    class MockToolResponse(BaseModel):
        success: bool = True
        output: Optional[str] = None
        message: Optional[str] = None

        @classmethod
        def error(cls, msg: str) -> "MockToolResponse":
            return cls(success=False, output=msg, message="ERROR")

    # Override the imported ToolRequest and ToolResponse for the testing scope
    ToolRequest = MockToolRequest
    ToolResponse = MockToolResponse

    # Mock the 'client' module and its GOOGLE_API_KEY
    class MockClient:
        def __init__(self, api_key: Optional[str]):
            self.GOOGLE_API_KEY = api_key

    # Temporarily define necessary config responses for local testing
    # In a real setup, these would be imported from multi_tool_agent.config.response
    GREETING_RESPONSES = {
        "morning": "Good morning! ☀️ Welcome to PlotBuddy! Let's craft an amazing story today.",
        "afternoon": "Good afternoon! 🌆 PlotBuddy is ready to help you write. What masterpiece will you create?",
        "evening": "Good evening! 🌙 Welcome to PlotBuddy. Let's make some magic happen before the day ends."
    }
    # For testing, FAQ_RESPONSES, STORY_TEMPLATES, ERROR_MESSAGES are not directly used in this agent's logic.

    # Set up logging for testing
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # --- Test 1: With a mock API key to enable LLM calls ---
    print("--- Test Set 1: With Mock API Key (LLM Enabled) ---")
    client = MockClient(api_key="MOCKED_API_KEY_FOR_TESTING_123") # Enable LLM path
    agent = GreetingAgent()

    test_queries_llm_enabled = [
        "Hi there!",
        "Good afternoon PlotBuddy",
        "hello",
        "howdy!",
        "plot buddy",
        "start",
        "let's start",
        "create story", # Test direct story creation intent
        "write me a story", # Test another story creation intent
        "tell me a story", # Test another story creation intent
        "random non-greeting text", # Should not be handled by GreetingAgent
        123 # Non-string input
    ]

    for query in test_queries_llm_enabled:
        print(f"\nQ: {query}")
        response = agent.process(ToolRequest(user_id="test_user_llm", input=query))

        if response.success:
            print(f"A (Output): {response.output}")
            if response.message:
                print(f"   (Message: {response.message})")
        else:
            print(f"A (Not Handled/Error): {response.output or response.message}")
        print("-" * 50)

    # --- Test 2: Without a mock API key (LLM Disabled, only fallbacks) ---
    print("\n--- Test Set 2: Without Mock API Key (LLM Disabled, Fallback Only) ---")
    client = MockClient(api_key=None) # Disable LLM path
    agent = GreetingAgent()

    test_queries_llm_disabled = [
        "Hi there!",
        "Good morning PlotBuddy",
        "hello",
        "create story", # Test direct story creation intent with fallback
        "random non-greeting text",
    ]

    for query in test_queries_llm_disabled:
        print(f"\nQ: {query}")
        response = agent.process(ToolRequest(user_id="test_user_fallback", input=query))

        if response.success:
            print(f"A (Output): {response.output}")
            if response.message:
                print(f"   (Message: {response.message})")
        else:
            print(f"A (Not Handled/Error): {response.output or response.message}")
        print("-" * 50)