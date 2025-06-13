from google.adk.agents import Agent
from pydantic import BaseModel
from typing import Optional

class PlotBuddyAgent(Agent):
    """Base class for all PlotBuddy agents"""
    def __init__(self, name: str, description: str):
        super().__init__(
            name=name,
            model="gemini-2.0-flash",
            description=description
        )