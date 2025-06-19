"""
PlotBuddy Multi-Agent System
Entry point for the agent system
"""

from typing import Dict, Any, Union
from .agents.orchestrator import OrchestratorAgent
from .models.schemas import ToolRequest, ToolResponse

def process_message(user_id: str, message: Union[str, Dict[str, Any]]) -> str:
    """
    Process a message through the agent system.
    
    Args:
        user_id: Unique identifier for the user
        message: Either a string message or dictionary of story parameters
        
    Returns:
        str: Response from the agent system
    """
    # Create a tool request
    request = ToolRequest.create(
        user_id=user_id,
        message=message
    )

    # Process through orchestrator and get response
    orchestrator = OrchestratorAgent()
    response = orchestrator.process_message(user_id, request)
    
    # Return response text
    return response.output if response.output else response.error