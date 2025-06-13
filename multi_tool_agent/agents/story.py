from typing import Dict, Optional, List, Tuple
from ..models.schemas import ToolRequest, ToolResponse
from .base import PlotBuddyAgent

class StoryAgentConfig:
    """Configuration for story generation"""
    genres: List[str] = [
        "Mystery", "Sci-Fi", "Fantasy", "Romance", 
        "Adventure", "Horror", "Comedy"
    ]
    
    moods: List[str] = [
        "mysterious", "whimsical", "dark", "romantic",
        "epic", "funny", "melancholic", "suspenseful"
    ]
    
    lengths: List[str] = [
        "micro", "short", "medium", "long"
    ]
    
    templates: Dict[str, str] = {
        "format_error": """
📝 Please format your story request as:
genre | mood | length

Example: Mystery | suspenseful | micro
        
Available options:
🎭 Genres: {genres}
🌟 Moods: {moods}
📏 Lengths: {lengths}
""",
        "invalid_genre": "⚠️ Invalid genre. Available genres: {genres}",
        "invalid_mood": "⚠️ Invalid mood. Available moods: {moods}",
        "invalid_length": "⚠️ Invalid length. Available lengths: {lengths}"
    }

class StoryAgent(PlotBuddyAgent):
    def __init__(self):
        super().__init__(
            name="story_agent",
            description="Creates micro-stories based on user preferences."
        )
        self._config = StoryAgentConfig()

    def _validate_inputs(self, genre: str, mood: str, length: str) -> Tuple[bool, Optional[str]]:
        """Validate user inputs against available options"""
        genre_lower = genre.lower()
        mood_lower = mood.lower()
        length_lower = length.lower()

        if not any(g.lower() == genre_lower for g in self._config.genres):
            return False, self._config.templates["invalid_genre"].format(
                genres=", ".join(self._config.genres)
            )
            
        if not any(m.lower() == mood_lower for m in self._config.moods):
            return False, self._config.templates["invalid_mood"].format(
                moods=", ".join(self._config.moods)
            )
            
        if not any(l.lower() == length_lower for l in self._config.lengths):
            return False, self._config.templates["invalid_length"].format(
                lengths=", ".join(self._config.lengths)
            )
            
        return True, None

    def create_story(self, request: ToolRequest) -> ToolResponse:
        """Generate a story based on user preferences"""
        try:
            # Parse input
            parts = [p.strip() for p in request.input.split("|")]
            
            if len(parts) != 3:
                return ToolResponse(output=self._config.templates["format_error"].format(
                    genres=", ".join(self._config.genres),
                    moods=", ".join(self._config.moods),
                    lengths=", ".join(self._config.lengths)
                ))

            genre, mood, length = parts
            
            # Validate inputs
            is_valid, error_msg = self._validate_inputs(genre, mood, length)
            if not is_valid:
                return ToolResponse(output=error_msg)

            # Generate story
            story = (
                f"[{length.title()} {genre.title()} – {mood.title()}]\n\n"
                "It was closing time at the observatory when the last star winked out—and "
                "our clockmaker chased it into the sky...\n\n"
                "✨ The End ✨"
            )
            
            return ToolResponse(output=story)
            
        except Exception as e:
            return ToolResponse(output=f"⚠️ Error creating story: {str(e)}")

# For testing
if __name__ == "__main__":
    agent = StoryAgent()
    test_requests = [
        "Mystery|suspenseful|micro",
        "invalid|mood|length",
        "no separator here",
        "Fantasy|whimsical|short",
    ]
    
    print("🧪 Testing Story Agent\n")
    for req in test_requests:
        print(f"Request: {req}")
        response = agent.create_story(ToolRequest(user_id="test", input=req))
        print(f"\nResponse:\n{response.output}\n")
        print("-" * 50 + "\n")