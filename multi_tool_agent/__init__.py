"""
PlotBuddy Multi-Agent System
A modular story generation system using specialized agents.
"""

from .agent import process_message
from .models import ToolRequest, ToolResponse
from .agents import (
    GreetingAgent,
    FAQAgent,
    ProfileAgent,
    StoryAgent,
    OrchestratorAgent
)

__version__ = "1.0.0"

__all__ = [
    "process_message",     # Main entry point for processing messages
    "ToolRequest",         # Request model
    "ToolResponse",        # Response model
    "GreetingAgent",      # Handles greetings
    "FAQAgent",           # Answers questions
    "ProfileAgent",       # Manages user profiles
    "StoryAgent",         # Generates stories
    "OrchestratorAgent"   # Routes messages
]