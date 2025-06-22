"""
PlotBuddy Agent Manager
Centralizes agent initialization and coordination
"""

import logging
from typing import Optional, Dict, Any
import google.generativeai as genai
import re

from google.adk.agents import LlmAgent

logger = logging.getLogger(__name__)

from ..models.schemas import ToolRequest, ToolResponse
from .greeting import GreetingAgent
from .faq import FAQAgent
from .profile import ProfileAgent
from .story import StoryAgent

try:
    from . import client
    if hasattr(client, 'GOOGLE_API_KEY') and client.GOOGLE_API_KEY:
        genai.configure(api_key=client.GOOGLE_API_KEY)
        HAS_LLM_ACCESS = True
        logger.info("Google Generative AI API configured successfully in Orchestrator module.")
    else:
        HAS_LLM_ACCESS = False
        logger.warning("Google API key not found (via client), LLM features will be limited.")
except ImportError:
    client = None
    HAS_LLM_ACCESS = False
    logger.warning("Client module import failed, LLM features will be limited (in Orchestrator module).")

from multi_tool_agent.config.response import GREETING_RESPONSES, FAQ_RESPONSES, STORY_TEMPLATES, ERROR_MESSAGES

class OrchestratorAgent:
    """
    Manages the initialization and routing of messages to different PlotBuddy agents.
    """
    def __init__(self, model_name="gemini-2.0-flash"):
        self.model_name = model_name
        logger.info(f"OrchestratorAgent initialized with model: {model_name}")

        self.greeting_agent = GreetingAgent(model_name="gemini-1.5-flash")
        self.faq_agent = FAQAgent(model_name="gemini-1.5-flash")
        self.profile_agent = ProfileAgent(model_name="gemini-1.5-flash")
        self.story_agent = StoryAgent(model_name="gemini-2.0-flash")

        self.default_agent = self.greeting_agent

    def _route_message(self, request: ToolRequest) -> Any:
        """Route the message to the appropriate agent."""
        if not isinstance(request.input, str):
            logger.info("Structured input detected, routing to StoryAgent.")
            return self.story_agent

        message_lower = request.input.lower().strip()

        faq_patterns = [
            "help", "commands", "guide", "instruction", "price", "cost", "subscription", "pricing", "fee",
            "what genre", "available genre", "list of genre", "types of stories", "what stories",
            "how does it work", "how it works", "process", "hour", "time", "when are you open",
            "contact", "support", "email", "help me", "faq"
        ]
        if any(keyword in message_lower for keyword in faq_patterns):
            logger.info("✓ FAQ match → FAQAgent")
            return self.faq_agent

        greeting_keywords = ["hi", "hello", "hey", "good morning", "good afternoon", "good evening"]
        if any(keyword in message_lower for keyword in greeting_keywords):
            logger.info("✓ Greeting match → GreetingAgent")
            return self.greeting_agent

        story_keywords = ["create story", "write story", "generate story", "new story", "story"]
        if any(keyword in message_lower for keyword in story_keywords):
            logger.info("✓ Story creation match → StoryAgent")
            return self.story_agent
            
        logger.info("No specific agent match, routing to default (FAQAgent).")
        return self.faq_agent

    # --- FIX: RENAMED back to 'process' from 'process_message' ---
    # The signature (user_id, request, context) remains the same.
    def process(self, user_id: str, request: ToolRequest, context: Dict[str, Any] = None) -> ToolResponse:
        """
        Process an incoming message and route it to the appropriate agent.
        """
        logger.info(f"Orchestrator received and processing for user {user_id}: '{request.input}'")
        if context is None:
            context = {}

        message_lower = request.input.lower()
        story_creation_initial_keywords = ["create story", "write story", "make story", "story creation", "new story"]

        if any(keyword in message_lower for keyword in story_creation_initial_keywords) or message_lower.strip() == "story":
            logger.info(f"Initial story creation intent detected: '{request.input}'. Signaling frontend for redirect.")
            return ToolResponse(
                success=True,
                output="I'd love to help you create a story! Please tell me the genre, mood, and length.",
                message="REDIRECT_TO_STORY_CREATOR"
            )

        try:
            agent_to_use = self._route_message(request)
            logger.info(f"Routing to agent: {agent_to_use.__class__.__name__}")

            # All your specific agents (StoryAgent, GreetingAgent, etc.) are expected to have a 'process' method
            output = agent_to_use.process(request, context)
            
            return output
        except Exception as e:
            logger.error(f"Error processing message in Orchestrator's process: {e}", exc_info=True)
            return ToolResponse(
                success=False,
                output="I'm sorry, I encountered an internal error while trying to process your request. Please try again.",
                message=f"Orchestrator Error: {str(e)}"
            )

    def _detect_story_creation_intent(self, message: str, history: Dict[str, Any]) -> bool:
        """Detect if the user is intending to create or work on a story."""
        faq_indicators = [
            r"\b(?:plotbuddy|plot buddy|app|application|tool|platform|website)\b.*\b(?:use|using|work|help|question)\b",
            r"\b(?:how to|how do I|can I).*\b(?:plotbuddy|plot buddy|app|this)\b",
            r"\b(?:feature|function|button|menu|option)\b"
        ]

        for pattern in faq_indicators:
            if re.search(pattern, message.lower()):
                return False

        story_creation_patterns = [
            r"\b(?:create|make|write|start|build|develop) (?:a|the|my) (?:story|narrative|tale|novel|book)\b",
            r"\b(?:story idea|plot line|character development|setting|world ?building)\b",
            r"\b(?:protagonist|antagonist|hero|villain|conflict|resolution)\b",
            r"\bmy (?:story|book|novel|writing|manuscript)\b"
        ]

        for pattern in story_creation_patterns:
            if re.search(pattern, message.lower()):
                return True

        if history.get("story_context") and len(history["story_context"]) > 0:
            return True

        return False

    def _determine_best_agent(self, message: str, context: Dict[str, Any], history: Dict[str, Any]) -> str:
        """
        This method is not currently called by `process`, but if used,
        it helps determine the agent by string name.
        """
        try:
            faq_patterns = [
                r"\b(?:how do I|how to|what is|can I|does this|is there)\b",
                r"\b(?:faq|question|help|guide|tutorial)\b",
                r"\b(?:plotbuddy|plot buddy|app|application|tool|platform)\b",
                r"\?$"
            ]

            for pattern in faq_patterns:
                if re.search(pattern, message.lower()):
                    app_terms = ["plotbuddy", "plot buddy", "app", "application", "feature", "using"]
                    if any(term in message.lower() for term in app_terms):
                        logger.info("Detected application usage question, routing to FAQ agent")
                        return "faq"

            if self._detect_story_creation_intent(message, history):
                return "story"

            return "faq"
        except Exception as e:
            logger.error(f"Error in _determine_best_agent: {e}")
            return "faq"

    def use_llm_agent(self, request: ToolRequest, context: Dict[str, Any] = None) -> ToolResponse:
        """Use the LLM agent directly"""
        if context is None:
            context = {}
        if hasattr(self, 'llm_agent') and self.llm_agent:
             return self.llm_agent.process(request, context)
        else:
            logger.warning("use_llm_agent called but self.llm_agent is not defined in OrchestratorAgent.")
            return ToolResponse(success=False, output="LLM agent not available for direct use by Orchestrator.", message="LLM_NOT_CONFIGURED")


orchestrator = OrchestratorAgent()
