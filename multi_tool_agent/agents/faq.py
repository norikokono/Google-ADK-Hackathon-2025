from typing import Dict, Optional
from ..models.schemas import ToolRequest, ToolResponse
from .base import PlotBuddyAgent

class FAQAgentConfig:
    """Configuration for FAQ responses"""
    responses: Dict[str, str] = {
        "store hours": "🕒 We're open:\nMon-Fri: 9am-8pm\nSat: 10am-6pm\nSun: 11am-5pm",
        "pricing": "💰 Story Pricing:\n- Single story: $4.99\n- Story pack (5): $19.99\n- Story pack (10): $34.99",
        "genres": "📚 Available Genres:\n- Mystery & Thriller\n- Science Fiction\n- Fantasy\n- Romance\n- Adventure",
        "how it works": "✨ How PlotBuddy Works:\n1. Choose your genre\n2. Set the mood\n3. Pick story length\n4. Watch your story unfold!",
        "subscription": "🌟 Subscription Options:\n- Monthly (5 stories): $17.99\n- Quarterly (20 stories): $67.99\n- Annual (100 stories): $199.99"
    }
    
    keywords: Dict[str, list] = {
        "store hours": ["hours", "open", "closing", "time", "schedule"],
        "pricing": ["cost", "price", "pay", "charge", "fee"],
        "genres": ["genre", "type", "category", "story type", "kind"],
        "how it works": ["how", "work", "process", "steps", "guide"],
        "subscription": ["subscribe", "plan", "membership", "monthly", "yearly"]
    }

class FAQAgent(PlotBuddyAgent):
    def __init__(self):
        super().__init__(
            name="faq_agent",
            description="Handles frequently asked questions about the story service."
        )
        self._config = FAQAgentConfig()

    def _find_matching_topic(self, query: str) -> Optional[str]:
        """Find the best matching FAQ topic based on keywords"""
        query_lower = query.lower()
        
        # First try exact matches
        for topic in self._config.responses:
            if topic in query_lower:
                return topic
                
        # Then try keyword matches
        for topic, keywords in self._config.keywords.items():
            if any(kw in query_lower for kw in keywords):
                return topic
                
        return None

    def answer(self, request: ToolRequest) -> ToolResponse:
        """Process FAQ request and return appropriate response"""
        topic = self._find_matching_topic(request.input)
        
        if topic:
            return ToolResponse(output=self._config.responses[topic])
            
        # Fallback response with available topics
        fallback = (
            "I can help you with:\n"
            "- Store hours and schedule 🕒\n"
            "- Story pricing and packages 💰\n"
            "- Available genres 📚\n"
            "- How PlotBuddy works ✨\n"
            "- Subscription options 🌟\n\n"
            "What would you like to know about?"
        )
        return ToolResponse(output=fallback)

# For testing
if __name__ == "__main__":
    agent = FAQAgent()
    test_queries = [
        "What are your hours?",
        "How much does it cost?",
        "What genres do you have?",
        "How does this work?",
        "Tell me about subscriptions",
        "random question"
    ]
    
    for query in test_queries:
        print(f"\nQ: {query}")
        response = agent.answer(ToolRequest(user_id="test", input=query))
        print(f"A: {response.output}\n")
        print("-" * 50)