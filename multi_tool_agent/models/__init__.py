"""
PlotBuddy Models Package
Contains data models and schemas used across the multi-agent system.
"""

from .schemas import (
    ToolRequest,
    ToolResponse,
    AgentConfig
)

__all__ = [
    'ToolRequest',   # Request model for agent communication
    'ToolResponse',  # Response model for agent outputs
    'AgentConfig'    # Base configuration for agents
]