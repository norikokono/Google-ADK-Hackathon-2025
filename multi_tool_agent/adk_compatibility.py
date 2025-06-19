"""
ADK Compatibility Layer for PlotBuddy

This module provides a compatibility layer between PlotBuddy's multi-agent system
and the Google ADK (Agent Development Kit) framework.
"""

import logging
from typing import Callable, Dict, Any

logger = logging.getLogger(__name__)

# Import ADK libraries
try:
    from google.cloud.ai.generativelanguage.adk import agent
    logger.info("Successfully imported Google ADK agent module")
except ImportError:
    logger.warning("Google ADK agent module not found. Creating a mock version for development.")
    # Create a mock version of the agent for local development
    class _MockAgent:
        def orchestrator(self, func):
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)
            return wrapper
        
        def tool(self, func):
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)
            return wrapper
    
    agent = _MockAgent()

# Tool utilities for agent communication
class ToolManager:
    """Manages tools/agents and allows calling them with standardized interfaces."""
    
    def __init__(self):
        self._tools = {}
    
    def register(self, name: str, tool_func: Callable):
        """Register a tool function with a name."""
        self._tools[name] = tool_func
        logger.debug(f"Registered tool: {name}")
    
    def use(self, tool_name: str, request: Dict[str, Any]) -> Dict[str, Any]:
        """Use a tool by name with the given request."""
        if tool_name not in self._tools:
            logger.error(f"Unknown tool: {tool_name}")
            return {"output": f"Error: Tool '{tool_name}' not found", "success": False}
        
        try:
            # For agent tools, assume request is already in the right format
            # and they return a dict with at least an 'output' key
            logger.debug(f"Using tool: {tool_name}")
            result = self._tools[tool_name](request)
            return result
        except Exception as e:
            logger.exception(f"Error using tool {tool_name}: {e}")
            return {"output": f"Error: {str(e)}", "success": False}

# Create a global tool manager
tool = ToolManager()

# Register tools/agents
# This is typically done elsewhere in the codebase when agents are defined
# e.g., tool.register("greeting_agent", greeting_agent)

def init_adk_compatibility():
    """Initialize the ADK compatibility layer by registering all agents."""
    try:
        # Import and register all agents
        from multi_tool_agent.agents import TOOL_REGISTRY
        for name, tool_func in TOOL_REGISTRY.items():
            tool.register(name, tool_func)
        logger.info(f"Registered {len(TOOL_REGISTRY)} tools: {', '.join(TOOL_REGISTRY.keys())}")
        return True
    except Exception as e:
        logger.error(f"Failed to initialize ADK compatibility layer: {e}")
        return False

# Call init_adk_compatibility on import
try:
    init_adk_compatibility()
except ImportError:
    logger.warning("Could not initialize ADK compatibility layer - agents not registered yet.")