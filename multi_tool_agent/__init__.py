"""
PlotBuddy Multi-Agent System
"""

from .agent import process_message
from .agents import (
    GreetingAgent,
    FAQAgent,
    ProfileAgent,
    StoryAgent,
    ManagerAgent  # Changed from OrchestratorAgent
)

__all__ = [
    'process_message',
    'GreetingAgent',
    'FAQAgent',
    'ProfileAgent',
    'StoryAgent',
    'ManagerAgent'
]