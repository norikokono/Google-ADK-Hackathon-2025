from typing import Dict, Optional
from ..models.schemas import ToolRequest, ToolResponse
from .base import PlotBuddyAgent

class GreetingAgentConfig:
    """Configuration for greeting responses"""
    responses: Dict[str, str] = {
        # Standard greetings
        "hello": "👋 Hi there! I'm PlotBuddy, your story-crafting companion!",
        "hi": "✨ Hello! Ready to create some amazing stories together?",
        "hey": "🌟 Hey! I'm here to help bring your story ideas to life!",
        
        # Time-based greetings
        "good_morning": "🌅 Good morning! Let's start the day with some storytelling!",
        "good_afternoon": "☀️ Good afternoon! Ready for a creative adventure?",
        "good_evening": "🌙 Good evening! The perfect time for storytelling!",
        
        # Identity responses
        "name": "I'm PlotBuddy, your AI storytelling assistant! 📚",
        "identity": "I'm an AI storytelling companion, designed to help you create amazing micro-stories! ✍️",
        
        # Default/fallback
        "default": "Hello! I can help you create stories, explore genres, or answer questions about our service! 🎨"
    }
    
    # Keyword mappings for different response types
    keywords: Dict[str, list] = {
        "hello": ["hello", "hi", "hey", "greetings"],
        "name": ["your name", "who are you", "what are you"],
        "identity": ["what do you do", "tell me about yourself", "what can you do"]
    }

class GreetingAgent(PlotBuddyAgent):
    def __init__(self):
        super().__init__(
            name="greeting_agent",
            description="Handles greetings and introduces PlotBuddy's capabilities."
        )
        self._config = GreetingAgentConfig()

    def _get_response_type(self, message: str) -> str:
        """Determine the type of response needed based on the message"""
        message_lower = message.lower().strip()
        
        # Check for exact matches first
        if message_lower in self._config.responses:
            return message_lower
            
        # Check keyword mappings
        for response_type, keywords in self._config.keywords.items():
            if any(kw in message_lower for kw in keywords):
                return response_type
                
        return "default"

    def greet(self, request: ToolRequest) -> ToolResponse:
        """Process greeting request and return appropriate response"""
        response_type = self._get_response_type(request.input)
        response = self._config.responses.get(response_type, self._config.responses["default"])
        return ToolResponse(output=response)

# For testing
if __name__ == "__main__":
    agent = GreetingAgent()
    test_messages = [
        "hi",
        "hello",
        "what's your name?",
        "who are you?",
        "what do you do?",
        "good morning",
        "random message"
    ]
    
    for msg in test_messages:
        print(f"\nUser: {msg}")
        response = agent.greet(ToolRequest(user_id="test", input=msg))
        print(f"Bot: {response.output}")
        print("-" * 50)