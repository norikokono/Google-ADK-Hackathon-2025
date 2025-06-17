"""Configuration file containing response templates and messages for all agents"""

# Greeting Agent Responses - Simplified to match LLM style
GREETING_RESPONSES = {
    "morning": """👋 Good morning! I'm PlotBuddy, your creative writing assistant. Ready to bring your story ideas to life today! ✨

• Type `create story` to start writing
• Say `help` for more options
• Ask `what genres` for inspiration""",

    "afternoon": """👋 Good afternoon! I'm PlotBuddy, your creative writing assistant. Perfect time to create something amazing! ✨

• Type `create story` to start writing
• Say `help` for more options
• Ask `what genres` for inspiration""",

    "evening": """👋 Good evening! I'm PlotBuddy, your creative writing assistant. The perfect time for storytelling! ✍️

• Type `create story` to start writing
• Say `help` for more options
• Ask `what genres` for inspiration""",

    "welcome_back": """👋 Welcome back! PlotBuddy here, ready to continue our creative journey. ✨

• Type `create story` to pick up where we left off
• Say `help` for more options
• Ask `what genres` for inspiration"""
}

# Add the missing STORY_TEMPLATES dictionary
STORY_TEMPLATES = {
    "create_prompt": "✨ Let's create a {mood} {genre} story! How would you like it to begin?",
    "story_intro": "📝 Here's your {mood} {genre} story ({length})",
    "story_success": "✅ Your {mood} {genre} story has been created!",
    "story_retry": "🔄 Let me try another {mood} {genre} story for you...",
    "story_error": "❌ Sorry, I couldn't generate a {mood} {genre} story. Let's try again."
}

# FAQ Agent Responses
FAQ_RESPONSES = {
    "store_hours": "🕒 We're open:\nMon-Fri: 9am-8pm\nSat: 10am-6pm\nSun: 11am-5pm",
    "pricing": "💰 Story Pricing:\n- Single: $4.99\n- 5-pack: $19.99\n- 10-pack: $34.99",
    "subscription": "⭐ Subscriptions:\n- Monthly (5 stories): $17.99\n- Quarterly (20): $67.99"
}

# Common Error Messages
ERROR_MESSAGES = {
    "invalid_format": "⚠️ Please use the format: genre | mood | length",
    "profile_not_found": "😅 Profile not found. Would you like to create one?",
    "server_error": "🔧 Oops! Something went wrong. Please try again.",
    "unknown_command": "❓ I didn't understand that. Try 'help' for available commands."
}