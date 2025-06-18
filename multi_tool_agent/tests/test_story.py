"""Test the story agent functionality"""

import pytest
from multi_tool_agent.agents.story import StoryAgent

@pytest.mark.parametrize("params", [
    {"genre": "fantasy", "mood": "mysterious", "length": "short"},
    {"genre": "scifi", "mood": "tense", "length": "medium"}
])
def test_story_generator(params):
    """Test the StoryAgent functionality"""
    story_agent = StoryAgent()
    # Use the public method if available, otherwise keep _generate_story
    story = story_agent._generate_story(
        genre=params["genre"],
        mood=params["mood"],
        length=params["length"],
        user_id="test_user"
    )
    assert isinstance(story, str)
    assert len(story) > 0