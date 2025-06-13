"""
PlotBuddy Configuration Package
Contains configuration settings and response templates for all agents.
"""

from .responses import (
    GREETING_RESPONSES,
    FAQ_RESPONSES,
    STORY_TEMPLATES,
    ERROR_MESSAGES
)

__all__ = [
    'GREETING_RESPONSES',  # Greeting and introduction responses
    'FAQ_RESPONSES',      # Frequently asked questions and answers
    'STORY_TEMPLATES',    # Story generation templates
    'ERROR_MESSAGES'      # Standard error messages
]