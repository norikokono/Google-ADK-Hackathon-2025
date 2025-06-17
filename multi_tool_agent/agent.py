"""
PlotBuddy Multi-Agent System
Entry point for the agent system
"""

from typing import Dict, Any, Union
from .agents.manager import manager
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
    
    # Process through manager and get response
    response = manager.process_message(user_id, request)
    
    # Return response text
    return response.output if response.output else response.error
