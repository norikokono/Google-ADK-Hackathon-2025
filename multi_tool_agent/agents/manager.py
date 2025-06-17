"""
PlotBuddy Agent Manager
Centralizes agent initialization and coordination
"""

import logging
from typing import Optional, Dict, Any, Union
import google.generativeai as genai

logger = logging.getLogger(__name__)

# Local module imports
from ..models.schemas import ToolRequest, ToolResponse
from .greeting import GreetingAgent
from .faq import FAQAgent
from .profile import ProfileAgent
from .story import StoryAgent

# Import from your 'llms' directory - properly check for client availability
try:
    from . import client
    if hasattr(client, 'GOOGLE_API_KEY') and client.GOOGLE_API_KEY:
        genai.configure(api_key=client.GOOGLE_API_KEY)
        HAS_LLM_ACCESS = True
        logger.info("Google Generative AI API configured successfully")
    else:
        HAS_LLM_ACCESS = False
        logger.warning("Google API key not found, LLM features will be limited")
except ImportError:
    client = None
    HAS_LLM_ACCESS = False
    logger.warning("Client module import failed, LLM features will be limited")

from multi_tool_agent.config.response import GREETING_RESPONSES, FAQ_RESPONSES, STORY_TEMPLATES, ERROR_MESSAGES

class ManagerAgent:
    """
    Manages the initialization and routing of messages to different PlotBuddy agents.
    """
    def __init__(self):
        """
        Initializes all the individual PlotBuddy agents.
        """
        self.greeting_agent = GreetingAgent(model_name="gemini-2.0-flash")
        self.faq_agent = FAQAgent(model_name="gemini-2.0-flash")
        self.profile_agent = ProfileAgent(model_name="gemini-2.0-flash")
        self.story_agent = StoryAgent(model_name="gemini-2.0-flash")
        self.default_agent = self.greeting_agent
        logger.info("ManagerAgent initialized with all sub-agents")

    def _route_message(self, request: ToolRequest) -> Any:
        """Route the message to the appropriate agent."""
        if not isinstance(request.input, str):
            return self.story_agent  # Structured data is likely for story generation
            
        message_lower = request.input.lower().strip()
        
        # Check for FAQ patterns FIRST - these should have priority for informational queries
        faq_patterns = {
            "help": ["help", "commands", "guide", "instruction"],
            "pricing": ["price", "cost", "subscription", "pricing", "fee"],
            "genres": ["what genre", "available genre", "list of genre", "types of stories", "what stories"],
            "how": ["how does it work", "how it works", "process"],
            "hours": ["hour", "time", "when are you open"],
            "contact": ["contact", "support", "email", "help me"]
        }
        
        # Check FAQ patterns first
        for keywords in faq_patterns.values():
            if any(keyword in message_lower for keyword in keywords):
                logger.info("✓ FAQ match → FAQAgent")
                return self.faq_agent
        
        # Check for greeting patterns
        greeting_keywords = ["hi", "hello", "hey", "good morning", "good afternoon", "good evening"]
        if any(keyword in message_lower for keyword in greeting_keywords):
            logger.info("✓ Greeting match → GreetingAgent")
            return self.greeting_agent
        
        # If it's a story creation request
        story_keywords = ["create story", "write story", "generate story", "new story"]
        if any(keyword in message_lower for keyword in story_keywords):
            logger.info("✓ Story creation match → StoryAgent")
            return self.story_agent
        
        # Default to FAQ agent for unknown messages
        return self.faq_agent

    def process_message(self, user_id: str, request: ToolRequest) -> ToolResponse:
        logger.info(f"New message from {user_id}: '{request.input}'")
        
        agent_to_use = self._route_message(request)
        logger.info(f"Selected: {agent_to_use.__class__.__name__}")
        
        try:
            response = agent_to_use.process(request)
            logger.info(f"Response: {response.output or response.message}")
            return response
        except Exception as e:
            logger.error(f"Error in {agent_to_use.__class__.__name__}: {e}")
            return ToolResponse.error("I apologize, I'm having trouble understanding. Could you rephrase that?")

    def process(self, request: ToolRequest) -> ToolResponse:
        """Process the request by selecting the appropriate agent"""
        logger.info(f"Agent Manager received: '{request.input}'")
        
        # First try the greeting agent
        greeting_response = self.greeting_agent.process(request)
        logger.info(f"Greeting agent response: success={greeting_response.success}")
        
        # If greeting agent handled it successfully, return that response
        if greeting_response.success:
            return greeting_response
        
        # If not greeting, try the FAQ agent next
        logger.info(f"Trying FAQ agent for: '{request.input}'")
        faq_response = self.faq_agent.process(request)
        logger.info(f"FAQ agent response: success={faq_response.success}")
        
        # If FAQ handled it, return that
        if faq_response.success:
            return faq_response
        
        # If still not handled, try story agent or fall back to LLM
        # Process request with appropriate agent
        response = self.story_agent.process(request)
        
        # Store this response in the context for next request
        if not request.context:
            request.context = {}
        request.context["last_agent_response"] = response.output
        
        return response

# Singleton instance
manager = ManagerAgent()