from pydantic import BaseModel
from typing import Optional, Dict, Any

class ToolRequest(BaseModel):
    """Model for tool requests"""
    user_id: str
    input: str
    context: Optional[Dict[str, Any]] = None

    @classmethod
    def create(cls, user_id: str, message: str, **context) -> 'ToolRequest':
        """Create a new tool request with optional context"""
        return cls(user_id=user_id, input=message, context=context or None)

class ToolResponse(BaseModel):
    """Model for tool responses"""
    output: Optional[str] = None
    error: Optional[str] = None

    @classmethod
    def success(cls, message: str) -> 'ToolResponse':
        """Create a successful response"""
        return cls(output=message)

    @classmethod
    def error(cls, message: str) -> 'ToolResponse':
        """Create an error response"""
        return cls(error=message)

class AgentConfig(BaseModel):
    """Base configuration model for agents"""
    name: str
    description: str
    model: str = "gemini-2.0-flash"

    class Config:
        """Pydantic config"""
        frozen = True  # Makes config immutable