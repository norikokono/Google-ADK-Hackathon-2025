"""Configuration file containing response templates and messages for all agents"""

# Greeting Agent Responses
GREETING_RESPONSES = {
    "greeting": "👋 Hi there! I'm PlotBuddy, your story-crafting companion!",
    "name": "I'm PlotBuddy, your AI storytelling assistant! 📚",
    "help": "I can help you create stories, check your profile, or answer questions! ✨",
    "default": "Hello! How can I assist you with storytelling today? 🎨"
}

# FAQ Agent Responses
FAQ_RESPONSES = {
    "store_hours": "🕒 We're open:\nMon-Fri: 9am-8pm\nSat: 10am-6pm\nSun: 11am-5pm",
    "pricing": "💰 Story Pricing:\n- Single: $4.99\n- 5-pack: $19.99\n- 10-pack: $34.99",
    "subscription": "⭐ Subscriptions:\n- Monthly (5 stories): $17.99\n- Quarterly (20): $67.99"
}

# Story Agent Templates
STORY_TEMPLATES = {
    "format_guide": """
📝 Create your story using:
genre | mood | length

Examples:
- Mystery | suspenseful | micro
- Fantasy | whimsical | short
- Sci-Fi | dark | medium
    """,
    "story_header": "[{length} {genre} – {mood}]\n",
    "story_footer": "\n✨ The End ✨"
}

# Common Error Messages
ERROR_MESSAGES = {
    "invalid_format": "⚠️ Please use the format: genre | mood | length",
    "profile_not_found": "😅 Profile not found. Would you like to create one?",
    "server_error": "🔧 Oops! Something went wrong. Please try again.",
    "unknown_command": "❓ I didn't understand that. Try 'help' for available commands."
}