"""
PlotBuddy Multi-Agent System
Entry point for the agent system
"""

from typing import Dict, Any, Union
from .agents.orchestrator import OrchestratorAgent
from .models.schemas import ToolRequest, ToolResponse

# Singleton orchestrator instance (if appropriate)
orchestrator = OrchestratorAgent()

def process_message(user_id: str, message: Union[str, Dict[str, Any]]) -> str:
    """
    Process a message through the agent system.
    """
    # Create a tool request (adjust if .create does not exist)
    request = ToolRequest(user_id=user_id, input=message)
    response = orchestrator.process(request)
    # Return response text or error message
    return getattr(response, "output", None) or getattr(response, "error", "Unknown error")