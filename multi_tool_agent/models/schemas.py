# In multi_tool_agent/models/schemas.py

from pydantic import BaseModel, Field # Removed 'validator' for now
from typing import Optional, Dict, Any

class ToolRequest(BaseModel):
    """
    Model for tool requests.
    Includes a factory method `create` for convenience.
    """
    user_id: str
    input: Any  # Changed from str to Any to handle both string and dict inputs
    context: Optional[Dict[str, Any]] = None

    @classmethod
    def create(cls, user_id: str, message: Any, **context) -> 'ToolRequest':
        """
        Create a new tool request with optional context.
        This method is a factory to easily construct ToolRequest instances.
        """
        return cls(user_id=user_id, input=message, context=context or None)

class ToolResponse(BaseModel):
    """
    Model for tool responses.
    Includes factory methods for success and error responses.
    """
    success: bool = True
    data: Optional[str] = None
    message: Optional[str] = None
    output: Optional[str] = None  # Add this if your code needs "output"

    @classmethod
    def error(cls, msg: str) -> "ToolResponse":
        return cls(success=False, message=msg)

    @classmethod
    def success(cls, data: str = None, output: str = None, message: str = None) -> "ToolResponse":
        return cls(success=True, data=data, output=output, message=message)

class AgentConfig(BaseModel):
    """
    Base configuration model for agents.
    """
    name: str = Field(..., description="The name of the agent.")
    description: str = Field(..., description="A brief description of what the agent does.")
    model: str = Field("gemini-2.0-flash", description="The generative model to be used by the agent.")

    class Config:
        frozen = True

class StoryParameters(BaseModel):
    """Model for story generation parameters"""
    genre: str
    mood: str
    length: str
