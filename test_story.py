"""Test the story agent functionality"""

from multi_tool_agent.agents.story import StoryAgent
import os
import logging

logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def test_story_generator():
    """Test the StoryAgent functionality"""
    
    print("Initializing StoryAgent...")
    
    # Initialize the agent
    story_agent = StoryAgent()
    
    # Test parameters
    test_params = [
        {"genre": "fantasy", "mood": "mysterious", "length": "short"},
        {"genre": "scifi", "mood": "tense", "length": "medium"}
    ]
    
    # Generate test stories
    for params in test_params:
        print(f"\nGenerating {params['mood']} {params['genre']} story ({params['length']})...")
        
        story = story_agent._generate_story(
            genre=params["genre"],
            mood=params["mood"],
            length=params["length"],
            user_id="test_user"
        )
        
        print("\n" + "="*50)
        print(story)
        print("="*50 + "\n")

if __name__ == "__main__":
    # Check if API key is set
    api_key = os.environ.get("GOOGLE_API_KEY") or os.environ.get("GOOGLE_GENERATIVE_AI_API_KEY")
    if not api_key:
        print("WARNING: No Google API key found in environment variables.")
        print("Set GOOGLE_API_KEY or GOOGLE_GENERATIVE_AI_API_KEY before running.")
        exit(1)
        
    test_story_generator()