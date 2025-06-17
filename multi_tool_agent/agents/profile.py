import logging
from typing import Dict, Optional, Any

# Local module imports
from ..models.schemas import ToolRequest, ToolResponse
from . import client

# Third-party imports
from google.adk.agents import LlmAgent
from multi_tool_agent.config.response import GREETING_RESPONSES, FAQ_RESPONSES, STORY_TEMPLATES, ERROR_MESSAGES

logger = logging.getLogger(__name__)

class ProfileAgentConfig:
    """Configuration for profile management and response templates."""
    # Simulated user profiles
    profiles: Dict[str, Dict] = {
        "default": {
            "subscription": "Free Trial",
            "stories_remaining": 2,
            "favorite_genres": ["Mystery", "Sci-Fi"],
            "created_stories": 3,
            "member_since": "2024"
        },
        "user_123": {
            "subscription": "Pro Plan",
            "stories_remaining": 50,
            "favorite_genres": ["Fantasy", "Adventure", "Sci-Fi"],
            "created_stories": 15,
            "member_since": "2023"
        }
    }

    # Response templates with enhanced formatting
    templates: Dict[str, str] = {
        "profile_view": """
📊 **Your PlotBuddy Profile** 📊
---
👤 **Subscription**: {subscription}
📚 **Stories Remaining**: {stories_remaining}
❤️ **Favorite Genres**: {genres}
✍️ **Stories Created**: {created}
🗓️ **Member Since**: {member_since}
---
""",
        "error": "⚠️ Sorry, I encountered an error accessing your profile. Please try again later!"
    }

class ProfileAgent(LlmAgent):
    """
    An agent that manages user profiles, including subscription status,
    story credits, and other user-specific information.
    """
    def __init__(self, model_name: str = "gemini-2.0-flash"):
        """
        Initializes the ProfileAgent with its name, description, and LLM model.
        """
        # Call LlmAgent's constructor directly, providing a clear instruction
        super().__init__(
            model=model_name,
            name="profile_agent",
            description="Manages user profiles and provides information about subscriptions and usage.",
            instruction="You are a helpful profile management assistant for PlotBuddy. "
                        "Your sole purpose is to retrieve and display user profile information "
                        "such as subscription status, remaining story credits, favorite genres, "
                        "and membership duration. Present this information clearly and concisely."
        )
        self._config = ProfileAgentConfig()
        logger.info("ProfileAgent initialized.")

    def _get_user_profile(self, user_id: str) -> Dict[str, Any]:
        """
        Retrieves a user's profile data from the simulated storage.
        Returns the 'default' profile if the specific user_id is not found.
        """
        # In a real application, this would involve database queries or API calls
        return self._config.profiles.get(user_id, self._config.profiles["default"])

    def _format_profile(self, profile: Dict[str, Any]) -> str:
        """
        Formats the retrieved profile data into a user-friendly string
        using the predefined template.
        """
        # Join favorite genres into a comma-separated string for display
        genres_display = ", ".join(profile.get("favorite_genres", ["N/A"]))

        return self._config.templates["profile_view"].format(
            subscription=profile.get("subscription", "N/A"),
            stories_remaining=profile.get("stories_remaining", "N/A"),
            genres=genres_display,
            created=profile.get("created_stories", "N/A"),
            member_since=profile.get("member_since", "N/A")
        )

    def process(self, request: ToolRequest) -> ToolResponse:
        """
        Processes the incoming tool request to display the user's profile information.
        This method serves as the main entry point for the ProfileAgent.
        
        Args:
            request: A ToolRequest object containing the user's message and user_id.

        Returns:
            A ToolResponse object containing the formatted profile data on success,
            or an error message on failure.
        """
        logger.debug(f"ProfileAgent processing request for user_id: '{request.user_id}' with input: '{request.input}'")
        
        # For this agent, the input string (request.input) is often just a trigger.
        # The core logic relies on request.user_id to fetch the profile.
        
        try:
            profile = self._get_user_profile(request.user_id)
            response_text = self._format_profile(profile)
            logger.info(f"Successfully retrieved and formatted profile for user '{request.user_id}'.")
            # Return a successful ToolResponse with the formatted output
            return ToolResponse(success=True, output=response_text)
        except Exception as e:
            # Catch any unexpected errors during profile processing
            logger.error(f"Error processing profile for user {request.user_id}: {e}", exc_info=True)
            # Return an error ToolResponse with a user-friendly message
            return ToolResponse.error(message=self._config.templates["error"])

# For testing this agent in isolation
if __name__ == "__main__":
    # Mock ToolRequest and ToolResponse classes for standalone execution
    from pydantic import BaseModel
    class MockToolRequest(BaseModel):
        user_id: str
        input: Any
        context: Optional[Dict[str, Any]] = None

    class MockToolResponse(BaseModel):
        success: bool = True
        data: Optional[str] = None
        message: Optional[str] = None
        output: Optional[str] = None

        @classmethod
        def error(cls, msg: str) -> "MockToolResponse":
            return cls(success=False, message=msg)

    ToolRequest = MockToolRequest
    ToolResponse = MockToolResponse

    # Configure basic logging for visibility during testing
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    agent = ProfileAgent()
    test_cases = [
        ToolRequest(user_id="user_123", input="show my profile"),          # Should get specific user profile
        ToolRequest(user_id="unknown_user", input="profile please"),      # Should get default profile
        ToolRequest(user_id="default", input="subscription status"),      # Should get default profile
        ToolRequest(user_id="error_sim_user", input="simulate error")    # Will trigger the simulated error
    ]
    
    # Temporarily modify _get_user_profile to simulate an error for one test case
    original_get_user_profile = ProfileAgent._get_user_profile
    def mock_error_get_user_profile(self, user_id: str):
        if user_id == "error_sim_user":
            raise ValueError("Simulated profile retrieval error for testing.")
        return original_get_user_profile(self, user_id)
    
    ProfileAgent._get_user_profile = mock_error_get_user_profile # Apply the mock

    print("--- 🧪 Testing Profile Agent ---")
    for i, test in enumerate(test_cases):
        print(f"\n--- Test Case {i+1}: User: {test.user_id}, Input: '{test.input}' ---")
        response = agent.process(test)
        if response.success:
            print(f"**SUCCESS**\n{response.output}\n")
        else:
            print(f"**ERROR**\n{response.message}\n")
        print("-" * 60)

    # Restore the original method after testing to avoid side effects
    ProfileAgent._get_user_profile = original_get_user_profile