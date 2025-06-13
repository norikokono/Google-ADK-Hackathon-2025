from typing import Dict, Optional
from ..models.schemas import ToolRequest, ToolResponse
from .base import PlotBuddyAgent

class ProfileAgentConfig:
    """Configuration for profile management"""
    # Simulated user profiles
    profiles: Dict[str, Dict] = {
        "default": {
            "subscription": "Free Trial",
            "stories_remaining": 2,
            "favorite_genres": ["Mystery", "Sci-Fi"],
            "created_stories": 3,
            "member_since": "2024"
        }
    }
    
    # Response templates
    templates: Dict[str, str] = {
        "profile_view": """
📊 Profile Overview:
👤 Subscription: {subscription}
📚 Stories Remaining: {stories_remaining}
❤️ Favorite Genres: {genres}
✍️ Stories Created: {created}
🌟 Member Since: {member_since}
""",
        "not_found": "😅 Profile not found. Would you like to create one?",
        "error": "⚠️ Sorry, there was an error accessing your profile."
    }

class ProfileAgent(PlotBuddyAgent):
    def __init__(self):
        super().__init__(
            name="profile_agent",
            description="Manages user profiles and subscription information."
        )
        self._config = ProfileAgentConfig()

    def _get_user_profile(self, user_id: str) -> Dict:
        """Retrieve user profile or return default"""
        return self._config.profiles.get(user_id, self._config.profiles["default"])

    def _format_profile(self, profile: Dict) -> str:
        """Format profile data using template"""
        return self._config.templates["profile_view"].format(
            subscription=profile["subscription"],
            stories_remaining=profile["stories_remaining"],
            genres=", ".join(profile["favorite_genres"]),
            created=profile["created_stories"],
            member_since=profile["member_since"]
        )

    def get_profile(self, request: ToolRequest) -> ToolResponse:
        """Process profile request and return formatted response"""
        try:
            profile = self._get_user_profile(request.user_id)
            response = self._format_profile(profile)
            return ToolResponse(output=response)
        except Exception as e:
            return ToolResponse(output=self._config.templates["error"])

# For testing
if __name__ == "__main__":
    agent = ProfileAgent()
    test_cases = [
        ToolRequest(user_id="test_user", input="show my profile"),
        ToolRequest(user_id="unknown_user", input="profile please"),
        ToolRequest(user_id="default", input="subscription status")
    ]
    
    print("🧪 Testing Profile Agent\n")
    for test in test_cases:
        print(f"Testing user: {test.user_id}")
        response = agent.get_profile(test)
        print(response.output)
        print("-" * 50 + "\n")