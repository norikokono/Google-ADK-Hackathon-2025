"""
PlotBuddy Multi-Agent System
A modular story generation system using specialized agents for different tasks.
"""

from google.adk.agents import Agent
from pydantic import BaseModel, PrivateAttr
from typing import Optional, Dict, Any, List

# Move ToolRequest and ToolResponse to models/schemas.py
from models.schemas import ToolRequest, ToolResponse
from agents import (
    GreetingAgent, 
    FAQAgent,
    ProfileAgent,
    StoryAgent,
    OrchestratorAgent
)

# --- Initialize Agent System ---
def create_agent_system() -> OrchestratorAgent:
    """Initialize and connect all agents"""
    g_agent = GreetingAgent()
    f_agent = FAQAgent()
    p_agent = ProfileAgent()
    s_agent = StoryAgent()
    return OrchestratorAgent(g_agent, f_agent, p_agent, s_agent)

# Create single router instance
router = create_agent_system()

def process_message(user_id: str, message: str) -> str:
    """
    Process a user message through the multi-agent system.
    
    Args:
        user_id: Unique identifier for the user
        message: The user's input message
        
    Returns:
        str: The agent system's response
    """
