"""
PlotBuddy API Module
Manages the HTTP server, endpoints, and overall application configuration
for the PlotBuddy AI agents.
"""

# Import and expose the core application instance and the main entry point
# from the server module within this package.
from .server import app, main

# Define the public API of this package when using 'from agents import *'
__all__ = ['app', 'main']