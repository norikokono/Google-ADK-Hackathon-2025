"""
Test module for FAQAgent functionality
"""

import unittest
from unittest.mock import patch, MagicMock

from multi_tool_agent.agents.faq import FAQAgent
from multi_tool_agent.models.schemas import ToolRequest

class TestFAQAgent(unittest.TestCase):
    """Test cases for the FAQ Agent"""

    def setUp(self):
        """Set up the test environment"""
        self.agent = FAQAgent()

    def test_initialization(self):
        """Test that the agent initializes properly"""
        self.assertIsNotNone(self.agent)
        self.assertTrue(hasattr(self.agent, "name"))
        self.assertEqual(self.agent.name, "faq_agent")

    def test_basic_response(self):
        """Test basic question answering"""
        request = ToolRequest(
            user_id="test_user",
            input="What is PlotBuddy?"
        )
        response = self.agent.process(request)
        self.assertTrue(response.success)
        self.assertIsNotNone(response.output)
        self.assertGreater(len(response.output), 10)

    @patch('multi_tool_agent.agents.faq.genai')
    def test_ai_fallback(self, mock_genai):
        """Test AI fallback for unknown questions"""
        mock_response = MagicMock()
        mock_response.text = "This is a helpful answer about PlotBuddy."
        mock_genai.GenerativeModel.return_value.generate_content.return_value = mock_response

        request = ToolRequest(
            user_id="test_user",
            input="Can you explain how to create complex characters?"
        )
        response = self.agent.process(request)
        self.assertTrue(response.success)
        self.assertEqual(response.output, "This is a helpful answer about PlotBuddy.")

    def test_support_request(self):
        """Test handling of support requests"""
        request = ToolRequest(
            user_id="test_user",
            input="How do I contact support?"
        )
        response = self.agent.process(request)
        self.assertTrue(response.success)
        self.assertIn("support@plotbuddy.ai", response.output.lower())

    def test_empty_input(self):
        """Test handling of empty input"""
        request = ToolRequest(
            user_id="test_user",
            input=""
        )
        response = self.agent.process(request)
        self.assertTrue(response.success)
        self.assertGreater(len(response.output), 5)

if __name__ == "__main__":
    unittest.main()