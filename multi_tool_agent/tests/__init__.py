"""
PlotBuddy Test Suite

This package contains all unit and integration tests for the PlotBuddy multi-agent system.
"""

import os

__all__ = []

def setup_test_environment():
    """Set up environment variables and configurations for testing"""
    os.environ["TESTING"] = "True"
    os.environ["GOOGLE_API_KEY"] = "test_api_key"  # Mock API key for tests

# Automatically set up the test environment when the test suite is imported
setup_test_environment()