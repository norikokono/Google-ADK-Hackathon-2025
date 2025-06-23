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

GENRE_KEYWORDS = [
    "fantasy", "mystery", "sci-fi", "science fiction", "romance", "adventure",
    "thriller", "horror", "historical", "comedy", "drama", "action", "fairy tale",
    "myth", "legend", "crime", "detective", "dystopian", "utopian", "paranormal",
    "western", "cyberpunk"  # Add more supported genres here
]
MOOD_KEYWORDS = [
    "happy", "exciting", "dark", "funny", "sad", "romantic", "mysterious", "adventurous", "scary", "uplifting"
]
LENGTH_KEYWORDS = [
    "short", "medium", "long"
]

def extract_param(keywords, message):
    for word in keywords:
        if word in message:
            return word
    return None

class OrchestratorAgent:
    """
    Manages the initialization and routing of messages to different PlotBuddy agents.
    """
    def __init__(self, model_name="gemini-2.0-flash"):
        self.model_name = model_name
        logger.info(f"OrchestratorAgent initialized with model: {model_name}")

        self.greeting_agent = GreetingAgent(model="gemini-1.5-flash")
        self.faq_agent = FAQAgent(model_name="gemini-1.5-flash")
        self.profile_agent = ProfileAgent(model_name="gemini-1.5-flash")
        self.story_agent = StoryAgent(model_name="gemini-2.0-flash")
        self.llm_agent = LlmAgent(
            name="llm_agent",
            model="gemini-1.5-flash",
            description="Handles open-ended user queries.",
            instruction="You are a helpful AI assistant."
        )

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

        story_keywords = ["create story", "write story", "generate story", "new story", "story", "plot", 
                          "character", "world building", "narrative", "novel", "book", "tale", "story idea",
                          "story creation", "make story", "develop story", "build story", "storytelling",
                          "story prompt", "story concept", "story outline", "story draft", "story structure",
                          "story arc", "story theme", "story genre", "story setting", "story character",
                          "story conflict", "story resolution", "story climax", "story beginning", 
                          "story middle", "story end", "story plot twist", "story character development",
                          "story dialogue", "story scene", "story chapter", "story summary", "story analysis",
                          "story feedback", "story review", "story brainstorming", "story inspiration",
                          "story writing", "story editing", "story publishing", "story sharing", "story collaboration",
                          "story workshop", "story community", "story writing tips", "story writing advice",
                          "story writing techniques", "story writing prompts", "story writing exercises"]
        if any(keyword in message_lower for keyword in story_keywords):
            logger.info("✓ Story creation match → StoryAgent")
            return self.story_agent
            
        logger.info("No specific agent match, routing to default (FAQAgent).")
        return self.faq_agent

    # --- FIX: RENAMED back to 'process' from 'process_message' ---
    # The signature (user_id, request, context) remains the same.
    def process(self, request: ToolRequest, context: dict = None) -> ToolResponse:
        """
        Process an incoming message and route it to the appropriate agent.
        """
        logger.info(f"Orchestrator received and processing: '{request.input}'")
        if context is None:
            context = {}

        message_lower = request.input.lower().strip()

        # 1. Story creation intent (redirect)
        story_creation_initial_keywords = [
            "create story", "write story", "make story", "story creation", "new story", "generate story"
        ]
        if any(keyword in message_lower for keyword in story_creation_initial_keywords) or message_lower == "story":
            return ToolResponse(
                success=True,
                output=None,
                message="REDIRECT_TO_STORY_CREATOR"
            )

        # 2. Supported genre: respond and redirect
        for genre in [
            "mystery", "scifi", "fantasy", "romance", "adventure", "horror",
            "comedy", "thriller", "historical", "western", "cyberpunk"
        ]:
            if genre in message_lower:
                return ToolResponse(
                    success=True,
                    output=(
                        f"Fantastic choice! 🌟 '{genre.title()}' stories are full of adventure and imagination. "
                        f"Let's get started—I'm sending you to the story creator!"
                    ),
                    message="REDIRECT_TO_STORY_CREATOR"
                )

        try:
            # FAQAgent first
            faq_response = self.faq_agent.process(request, context)
            if faq_response.success:
                return faq_response

            # GreetingAgent for greetings and small talk
            greeting_response = self.greeting_agent.process(request, context)
            if greeting_response.success:
                return greeting_response

            agent_to_use = self._route_message(request)
            logger.info(f"Routing to agent: {agent_to_use.__class__.__name__}")

            output = agent_to_use.process(request, context)

            # If the agent handled the request, return its response
            if output and output.success:
                return output

            # If FAQAgent didn't handle, try fallback to FAQAgent (if not already tried)
            if agent_to_use is not self.faq_agent:
                faq_output = self.faq_agent.process(request, context)
                if faq_output and faq_output.success:
                    return faq_output

            # LLM fallback for open-ended queries
            if hasattr(self, "llm_agent") and self.llm_agent:
                llm_response = self.llm_agent.process(request, context)
                if llm_response and getattr(llm_response, "output", None):
                    return llm_response

            # Final fallback
            return ToolResponse(
                success=False,
                output=None,
                message="I'm here to help! Could you please rephrase your question or let me know what kind of story you'd like to create?"
            )

        except Exception as e:
            logger.error(f"Error processing message in Orchestrator's process: {e}", exc_info=True)
            message_lower = request.input.lower().strip()

            # Engaging fallbacks for common topics
            from multi_tool_agent.config.response import FAQ_RESPONSES
            if "genre" in message_lower or "genres" in message_lower:
                # Use LLM for a more engaging, personalized response
                if hasattr(self, "run"):
                    prompt = (
                        "The user is interested in story genres. "
                        "Respond enthusiastically, suggest a few fun genres, and ask which one they'd like to try. "
                        "Encourage them to pick a genre to start their story."
                    )
                    llm_response = self.run(prompt=prompt + f"\nUser: {request.input}\nAssistant:")
                    output = getattr(llm_response, "output", None) or getattr(llm_response, "text", None)
                    if output:
                        return ToolResponse(success=True, output=output, message="GENRES_MESSAGE")
                # Fallback to static
                return ToolResponse(success=True, output=FAQ_RESPONSES["GENRES_MESSAGE"], message="")

            if "brainstorm" in message_lower or "idea" in message_lower:
                if hasattr(self, "run"):
                    prompt = (
                        "The user wants to brainstorm story ideas. "
                        "Ask an engaging follow-up question, suggest creative directions, and keep the conversation going. "
                        "Be friendly and encouraging."
                    )
                    llm_response = self.run(prompt=prompt + f"\nUser: {request.input}\nAssistant:")
                    output = getattr(llm_response, "output", None) or getattr(llm_response, "text", None)
                    if output:
                        return ToolResponse(success=True, output=output, message="BRAINSTORM_MESSAGE")
                return ToolResponse(success=True, output="Let's brainstorm together! Tell me a theme, genre, or idea, and I'll help you get started.", message="BRAINSTORM_MESSAGE")
            if "price" in message_lower or "pricing" in message_lower or "cost" in message_lower or "subscription" in message_lower:
                return ToolResponse(
                    success=True,
                    output="PlotBuddy offers a free trial and affordable subscription options. Visit the pricing page or ask me for details about our plans!",
                    message="PRICING_MESSAGE"
                )
            if "help" in message_lower:
                return ToolResponse(
                    success=True,
                    output="I'm here to help! You can ask me to create a story, brainstorm ideas, or learn about genres and features. What would you like to do?",
                    message="HELP_MESSAGE"
                )

            # Friendly generic fallback
            return ToolResponse(
                success=False,
                output=None,
                message="I'm here to help! Could you please rephrase your question or let me know what kind of story you'd like to create?"
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
        """Use the LLM agent directly for open-ended queries or when no other agent is suitable."""
        if context is None:
            context = {}
        if hasattr(self, 'llm_agent') and self.llm_agent:
            llm_response = self.llm_agent.process(request, context)
            return llm_response

        # If LLM agent fails, then:
        return ToolResponse(
            success=False,
            output=None,
            message="I'm here to help! Could you please rephrase your question or let me know what kind of story you'd like to create?"
        )

    def brainstorm_with_llm(self, request: ToolRequest, context: Dict[str, Any] = None) -> ToolResponse:
        """Use the LLM agent for brainstorming to keep the conversation going."""
        if context is None:
            context = {}
        if hasattr(self, "llm_agent") and self.llm_agent:
            prompt = (
                "You are PlotBuddy, a creative writing assistant. "
                "The user wants to brainstorm story ideas. "
                "Ask engaging follow-up questions, suggest creative directions, and keep the conversation going. "
                "Be friendly and encouraging."
            )
            # Optionally, include the user's input in the prompt
            user_input = request.input
            full_prompt = f"{prompt}\nUser: {user_input}\nAssistant:"
            llm_response = self.llm_agent.run(prompt=full_prompt)
            output = getattr(llm_response, "output", None) or getattr(llm_response, "text", None)
            if output:
                return ToolResponse(success=True, output=output, message="BRAINSTORM_CONVERSATION")

        return ToolResponse(
            success=False,
            output=None,
            message="I'm here to help! Could you please rephrase your question or let me know what kind of story you'd like to create?"
        )


orchestrator = OrchestratorAgent()