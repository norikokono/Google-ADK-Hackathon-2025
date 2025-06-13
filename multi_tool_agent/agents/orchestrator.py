from typing import Dict, Any
from pydantic import BaseModel, PrivateAttr
from ..models.schemas import ToolRequest, ToolResponse
from .base import PlotBuddyAgent

class OrchestratorConfig(BaseModel):
    """Configuration for agent routing"""
    _greeting_agent: Any = PrivateAttr(default=None)
    _faq_agent: Any = PrivateAttr(default=None)
    _profile_agent: Any = PrivateAttr(default=None)
    _story_agent: Any = PrivateAttr(default=None)

    routing_keywords: Dict[str, list] = {
        "greeting": ["hi", "hello", "hey", "morning", "afternoon", "evening"],
        "story": ["create story", "write story", "new story", "|"],
        "profile": ["profile", "account", "subscription", "remaining"],
        "faq": ["how", "what", "when", "where", "why", "cost", "price", "hours"]
    }

class OrchestratorAgent(PlotBuddyAgent):
    def __init__(self, greeting, faq, profile, story):
        """Initialize orchestrator with sub-agents"""
        super().__init__(
            name="orchestrator",
            description="Routes user queries to specialized sub-agents"
        )
        self._config = OrchestratorConfig()
        self._config.__dict__['_private_attributes'].update({
            '_greeting_agent': greeting,
            '_faq_agent': faq,
            '_profile_agent': profile,
            '_story_agent': story
        })

    def _get_intent(self, message: str) -> str:
        """Determine user intent from message"""
        msg_lower = message.lower().strip()
        
        for intent, keywords in self._config.routing_keywords.items():
            if any(kw in msg_lower for kw in keywords):
                return intent
                
        return "unknown"

    def route(self, request: ToolRequest) -> ToolResponse:
        """Route request to appropriate agent"""
        intent = self._get_intent(request.input)
        agents = self._config.__dict__['_private_attributes']

        try:
            if intent == "greeting":
                return agents['_greeting_agent'].greet(request)
                
            if intent == "story":
                return agents['_story_agent'].create_story(request)
                
            if intent == "profile":
                return agents['_profile_agent'].get_profile(request)
                
            if intent == "faq":
                return agents['_faq_agent'].answer(request)
                
            # Fallback to FAQ for unknown intents
            return ToolResponse(output=(
                "I can help you with:\n"
                "✍️ Creating stories (say 'create story')\n"
                "👤 Checking your profile\n"
                "❓ Answering questions about our service\n"
                "What would you like to do?"
            ))
            
        except Exception as e:
            return ToolResponse(
                error=f"Error processing request: {str(e)}"
            )

# For testing
if __name__ == "__main__":
    from .greeting import GreetingAgent
    from .faq import FAQAgent
    from .profile import ProfileAgent
    from .story import StoryAgent
    
    # Initialize test agents
    g_agent = GreetingAgent()
    f_agent = FAQAgent()
    p_agent = ProfileAgent()
    s_agent = StoryAgent()
    
    # Create orchestrator
    orchestrator = OrchestratorAgent(g_agent, f_agent, p_agent, s_agent)
    
    # Test messages
    test_messages = [
        "hi there",
        "what are your hours?",
        "create story",
        "Mystery|spooky|short",
        "show my profile",
        "random message"
    ]
    
    # Run tests
    print("🤖 Testing Orchestrator\n")
    for msg in test_messages:
        print(f"User: {msg}")
        response = orchestrator.route(ToolRequest(user_id="test", input=msg))
        print(f"Bot: {response.output or response.error}\n")
        print("-" * 50)