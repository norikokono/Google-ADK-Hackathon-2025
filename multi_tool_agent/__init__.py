"""
PlotBuddy Multi-Agent System
A multi-agent system for creative writing assistance.
"""

# Version information
__version__ = "1.0.0"

# Import the main entry point
from .agent import process_message

# Make process_message available at the package level
__all__ = ["process_message"]