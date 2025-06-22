import logging
import time
import google.generativeai as genai
import random
from datetime import datetime
from typing import Dict, Any, List, Optional
from ..models.schemas import ToolRequest, ToolResponse
from google.adk.agents import LlmAgent

try:
    from . import client
except ImportError:
    client = None

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class ProfileAgent:
    """Agent that serves as a personal creative coach, providing varied advice and support."""

    def __init__(self, model_name="gemini-1.5-flash"):
        self.model_name = model_name
        logger.info(f"ProfileAgent initialized with model: {model_name}")
        self.user_profiles = {}  # Store user profiles
        self.interaction_history = {}  # Track interactions to prevent repetition
        
        self.coaching_approaches = [
            "socratic", "structural", "motivational", "technical",
            "explorative", "reflective", "analytical", "contrasting"
        ]

    def process(self, request: ToolRequest) -> ToolResponse:
        user_id = request.user_id or "anonymous_user"
        user_message = request.input.strip() if request.input else ""
        context = request.context or {}
        
        profile = self._get_user_profile(user_id)

        if user_id not in self.interaction_history:
            self.interaction_history[user_id] = {
                "last_approaches": [],
                "last_topics": [],
                "last_advice": [],
                "interaction_count": 0
            }
        
        history = self.interaction_history[user_id]
        history["interaction_count"] += 1
        
        if context.get("brainstorm"):
            return self._provide_creative_coaching(user_id, profile, context, history)
        if context.get("advice"):
            return self._provide_contextual_advice(user_id, profile, context, history)
        if user_message.lower().startswith("/profile"):
            return self._handle_profile_command(user_id, user_message, profile)
        if any(keyword in user_message.lower() for keyword in ["stuck", "advice", "help", "idea", "suggestion", "feedback"]):
            extracted_topic = self._extract_topic(user_message)
            return self._provide_creative_coaching(user_id, profile, {"topic": extracted_topic}, history)
        return self._handle_general_query(user_id, user_message, profile, history)
    
    def _create_initial_profile(self) -> Dict[str, Any]:
        return {
            "created_at": datetime.now(),
            "last_updated": datetime.now(),
            "personal_info": {
                "name": "",
                "display_name": "",
                "email": ""
            },
            "creative_preferences": {
                "domains": [],
                "genres": [],
                "themes": [],
                "creative_process": "",
                "feedback_style": "balanced"
            },
            "creative_goals": {
                "current_project": "",
                "short_term": [],
                "long_term": [],
                "challenges": []
            },
            "stats": {
                "coaching_sessions": 0,
                "projects_completed": 0,
                "last_activity": datetime.now()
            }
        }
    
    def _select_coaching_approach(self, history: Dict[str, Any]) -> str:
        recent_approaches = history.get("last_approaches", [])
        available_approaches = [a for a in self.coaching_approaches if a not in recent_approaches]
        if not available_approaches:
            available_approaches = self.coaching_approaches
        selected_approach = random.choice(available_approaches)
        recent_approaches.append(selected_approach)
        if len(recent_approaches) > 3:
            recent_approaches.pop(0)
        history["last_approaches"] = recent_approaches
        return selected_approach
    
    def _provide_creative_coaching(self, user_id: str, profile: Dict[str, Any], context: Dict[str, Any], history: Dict[str, Any]) -> ToolResponse:
        genre = context.get("genre", "")
        mood = context.get("mood", "")
        topic = context.get("topic", "")
        profile["stats"]["coaching_sessions"] += 1
        profile["stats"]["last_activity"] = datetime.now()
        approach = self._select_coaching_approach(history)
        try:
            domains = ", ".join(profile["creative_preferences"]["domains"]) if profile["creative_preferences"]["domains"] else "various"
            genres = ", ".join(profile["creative_preferences"]["genres"]) if profile["creative_preferences"]["genres"] else genre or "any"
            process = profile["creative_preferences"]["creative_process"] or "flexible"
            approach_prompts = {
                "socratic": f"As a creative coach using the Socratic approach, ask 2-3 thought-provoking questions about their {genres} project. Avoid giving direct answers.",
                "structural": f"As a creative coach focusing on structure, provide 1-2 organizational techniques for {genres} creation.",
                "motivational": f"As a motivational coach, encourage and give perspective on challenges in {genres} creation. Include a reframing example.",
                "technical": f"As a technical coach, share 1-2 actionable techniques for a {genres} project.",
                "explorative": f"As an explorative coach, suggest 2-3 unconventional directions for their {genres} project.",
                "reflective": f"As a reflective coach, guide the creator to examine their own creative process in {genres} work. Suggest a specific reflective exercise or journaling prompt.",
                "analytical": f"As an analytical coach, provide a framework for evaluating their current {genres} project. Suggest 2-3 specific elements they might analyze.",
                "contrasting": f"As a coach using contrasting perspectives, present two different approaches to a common challenge in {genres} creation. Highlight the benefits of each approach."
            }
            
            prompt = f"""
            You are a creative coach specializing in helping creators with their projects.
            
            Creator is working on: {genre} {mood} {topic}
            Creator's preferred domains: {domains}
            Creator's process style: {process}
            
            {approach_prompts[approach]}
            
            Important coaching guidelines:
            1. Be concise and practical (max 3-4 sentences)
            2. Focus on the creator's agency and decision-making power
            3. Ask at least one open-ended question to encourage reflection
            4. This is interaction #{history["interaction_count"]} with this creator
            5. Avoid repeating advice you've given before
            6. Don't provide creative content directly (no story ideas, character concepts, etc.)
            7. Ensure your advice is different from previous guidance
        
            Your response:
            """
            
            model = genai.GenerativeModel(self.model_name)
            response = model.generate_content(prompt)
            
            output = response.text.strip()
            
            recent_advice = history.get("last_advice", [])
            recent_advice.append(output[:100])
            if len(recent_advice) > 5:
                recent_advice.pop(0)
            history["last_advice"] = recent_advice
            
            return ToolResponse(
                success=True,
                output=output
            )
        except Exception as e:
            logger.error(f"Error providing creative coaching: {e}")
            
            fallback_responses = {
                "socratic": f"What aspect of your {genre} project feels most challenging right now? Have you considered how your audience might experience the {mood} elements you're incorporating?",
                "structural": f"For {genre} projects, creating a visual map of key elements can help see connections. Try arranging your main components on paper and drawing relationships between them.",
                "motivational": f"Every creator faces moments of uncertainty. Your unique perspective is what will make this {genre} project special. What initially inspired you to explore this idea?",
                "technical": f"The 'reverse outline' technique can be helpful when you feel stuck. Try summarizing each section of your work and analyzing how they connect to your overall vision.",
                "explorative": f"What if you approached your {genre} project from an unexpected viewpoint? Consider how a different emotional tone might transform your current direction.",
                "reflective": f"Reflect on previous creative challenges you've overcome. What strategies worked well then that might help with your current {genre} project?",
                "analytical": f"Consider analyzing the pacing of your {genre} piece. Are there sections that could benefit from expansion or condensing to enhance the {mood} quality you're aiming for?",
                "contrasting": f"Some creators prefer detailed planning before creating, while others discover through the creation process itself. Which approach tends to yield better results for your {genre} work?"
            }
            
            return ToolResponse(
                success=True,
                output=fallback_responses.get(approach, "What specific aspect of your creative project would you like guidance on today?")
            )
    
    def _provide_contextual_advice(self, user_id: str, profile: Dict[str, Any], context: Dict[str, Any], history: Dict[str, Any]) -> ToolResponse:
        context_type = context.get("context", "")
        genre = context.get("genre", "")
        mood = context.get("mood", "")
        
        approach = self._select_coaching_approach(history)
        
        try:
            context_prompts = {
                "story_creation": f"""
                    The creator is starting a new {genre} story with a {mood} tone.
                    Focus your coaching on the initial ideation and concept development process.
                """,
                "character_development": f"""
                    The creator is developing characters for their {genre} story with a {mood} tone.
                    Focus your coaching on character depth, motivation, and authenticity.
                """,
                "worldbuilding": f"""
                    The creator is building a world for their {genre} story with a {mood} atmosphere.
                    Focus your coaching on creating cohesive, engaging settings that support their narrative.
                """,
                "plot_structure": f"""
                    The creator is working on the plot structure for their {genre} story with a {mood} tone.
                    Focus your coaching on narrative flow, pacing, and meaningful conflict.
                """,
                "revision": f"""
                    The creator is revising their {genre} story with a {mood} tone.
                    Focus your coaching on effective editing strategies and maintaining narrative cohesion.
                """
            }
            
            context_prompt = context_prompts.get(context_type, f"""
                The creator is working on a {genre} project with a {mood} tone.
                Focus your coaching on providing general creative guidance that's immediately applicable.
            """)
            
            prompt = f"""
            You are a creative coach specializing in helping creators with their projects.
            
            {context_prompt}
            
            Using the {approach} coaching approach:
            1. Provide brief, targeted advice (2-3 sentences)
            2. Include one specific technique or exercise they could try
            3. Ask one thought-provoking question to stimulate their creativity
            4. This is interaction #{history["interaction_count"]} with this creator
            
            Important:
            - Be concise and immediately practical
            - Frame advice in terms of process rather than content
            - Don't provide actual creative content (no story ideas, character concepts, etc.)
            - Ensure your advice is different from previous guidance
            - Avoid repeating similar advice given in the last 5 interactions
            - Do not use Markdown formatting
            - Do not use formatting symbols (e.g., *, _, or ) for bolding or italicizing—output should be plain text
            - Support the user's storytelling process, not developer-facing tools or services.
            
            Your response:
            """
            
            model = genai.GenerativeModel(self.model_name)
            response = model.generate_content(prompt)
            
            output = response.text.strip()
            
            recent_advice = history.get("last_advice", [])
            recent_advice.append(output[:100])
            if len(recent_advice) > 5:
                recent_advice.pop(0)
            history["last_advice"] = recent_advice
            
            return ToolResponse(
                success=True,
                output=output
            )
        except Exception as e:
            logger.error(f"Error providing contextual advice: {e}")
            
            fallbacks = [
                f"Consider how the {mood} elements in your {genre} piece could be enhanced through sensory details. What emotions are you hoping your audience will experience?",
                f"Try the 'opposite exercise' - briefly imagine your {genre} piece with the opposite {mood} tone. What insights does this contrast reveal about your creative intentions?",
                f"For your {genre} project, you might benefit from creating a mind map of connected elements. How do the various components of your work reinforce the {mood} quality you're aiming for?",
                f"Creative rhythm often involves alternating between focused work and reflective distance. Would stepping back from your {genre} project for a short while give you fresh perspective?",
                f"Consider how your own experiences might authentically inform the {mood} aspects of your {genre} work. What personal insights could add depth to your creation?"
            ]
            
            return ToolResponse(
                success=True,
                output=random.choice(fallbacks)
            )
    
    def _handle_profile_command(self, user_id: str, message: str, profile: Dict[str, Any]) -> ToolResponse:
        parts = message.split(maxsplit=2)
        command = parts[1].lower() if len(parts) > 1 else "view"
        
        if command == "view":
            return ToolResponse(
                success=True,
                output=self._generate_profile_summary(profile)
            )
        elif command == "set" and len(parts) > 2:
            try:
                setting = parts[2].strip()
                return self._update_profile_settings(user_id, setting, profile)
            except Exception as e:
                logger.error(f"Error updating profile: {e}")
                return ToolResponse(
                    success=False,
                    output="I couldn't update your profile settings. Please try again with a format like '/profile set name John' or '/profile set genre fantasy'."
                )
        else:
            return ToolResponse(
                success=True,
                output=("Profile commands:\n"
                        "• /profile view - See your creative profile\n"
                        "• /profile set [field] [value] - Update a preference\n"
                        "• Examples: '/profile set genre fantasy', '/profile set process outliner'")
            )
    
    def _handle_general_query(self, user_id: str, message: str, profile: Dict[str, Any], history: Dict[str, Any]) -> ToolResponse:
        approach = self._select_coaching_approach(history)
        
        try:
            domains = ", ".join(profile["creative_preferences"]["domains"]) if profile["creative_preferences"]["domains"] else "various"
            genres = ", ".join(profile["creative_preferences"]["genres"]) if profile["creative_preferences"]["genres"] else "various"
            
            prompt = f"""
            You are a creative coach speaking with a creator.
            
            Creator's message: "{message}"
            Creator's preferred domains: {domains}
            Creator's preferred genres: {genres}
            Coaching approach to use: {approach}
            
            Respond to their message from a creative coaching perspective:
            1. Keep your response concise (2-4 sentences)
            2. Be supportive and action-oriented
            3. Ask a question that promotes creative thinking
            4. This is interaction #{history["interaction_count"]} with this creator
            
            Important:
            - If their message isn't about creative work, respond with "GENERAL_QUERY"
            - Focus on process, not generating content for them
            - Provide different advice than you have before
            - Do not use Markdown formatting
            - Do not use formatting symbols (e.g., *, _, or ) for bolding or italicizing—output should be plain text
            - Support the user's storytelling process, not developer-facing tools or services.
            
            Your response:
            """
            
            model = genai.GenerativeModel(self.model_name)
            response = model.generate_content(prompt)
            
            output = response.text.strip()
            
            if "GENERAL_QUERY" in output:
                return ToolResponse(
                    success=False,
                    message="Not a creative coaching related message"
                )
            
            recent_advice = history.get("last_advice", [])
            recent_advice.append(output[:100])
            if len(recent_advice) > 5:
                recent_advice.pop(0)
            history["last_advice"] = recent_advice
            
            return ToolResponse(
                success=True,
                output=output
            )
            
        except Exception as e:
            logger.error(f"Error handling general query: {e}")
            return ToolResponse(
                success=False,
                message="Error processing query"
            )
    
    def _extract_topic(self, message: str) -> str:
        lower_msg = message.lower()
        
        topic = ""
        topic_indicators = [
            "about", "on", "for", 
            "with", "help me with", "advice on",
            "stuck on", "working on", "creating"
        ]
        
        for indicator in topic_indicators:
            if indicator in lower_msg:
                parts = lower_msg.split(indicator, 1)
                if len(parts) > 1:
                    topic = parts[1].strip()
                    break
        
        return topic
    
    def _update_profile_settings(self, user_id: str, setting: str, profile: Dict[str, Any]) -> ToolResponse:
        setting_lower = setting.lower()
        profile["last_updated"] = datetime.now()
        
        if setting_lower.startswith("name "):
            name = setting[5:].strip()
            profile["personal_info"]["name"] = name
            return ToolResponse(
                success=True,
                output=f"I've updated your name to '{name}' in your creative profile."
            )
            
        elif setting_lower.startswith("domain ") or setting_lower.startswith("domains "):
            domain = setting.split(" ", 1)[1].strip()
            if domain and domain not in profile["creative_preferences"]["domains"]:
                profile["creative_preferences"]["domains"].append(domain)
            return ToolResponse(
                success=True,
                output=f"I've added '{domain}' to your creative domains. Your current domains are: {', '.join(profile['creative_preferences']['domains'])}"
            )
                
        elif setting_lower.startswith("genre "):
            genre = setting_lower.split("genre ", 1)[1].strip()
            if genre and genre not in profile["creative_preferences"]["genres"]:
                profile["creative_preferences"]["genres"].append(genre)
            return ToolResponse(
                success=True,
                output=f"I've added '{genre}' to your preferred genres. Your current genres are: {', '.join(profile['creative_preferences']['genres'])}"
            )
                
        elif setting_lower.startswith("process "):
            process = setting_lower.split("process ", 1)[1].strip()
            profile["creative_preferences"]["creative_process"] = process
            return ToolResponse(
                success=True,
                output=f"Your creative process preference has been updated to '{process}'. I'll tailor my coaching accordingly."
            )
            
        elif setting_lower.startswith("feedback "):
            feedback = setting_lower.split("feedback ", 1)[1].strip()
            profile["creative_preferences"]["feedback_style"] = feedback
            return ToolResponse(
                success=True,
                output=f"Your feedback style preference has been updated to '{feedback}'. I'll adjust my coaching approach to match."
            )
            
        elif setting_lower.startswith("goal ") or setting_lower.startswith("challenge "):
            category = "short_term" if "short" in setting_lower else "challenges" if "challenge" in setting_lower else "long_term"
            value = setting.split(" ", 1)[1].strip()
            
            if value and value not in profile["creative_goals"][category]:
                profile["creative_goals"][category].append(value)
            
            category_name = "short-term goal" if category == "short_term" else "long-term goal" if category == "long_term" else "creative challenge"
            return ToolResponse(
                success=True,
                output=f"I've added '{value}' to your {category_name}s. I'll keep this in mind during our coaching sessions."
            )
            
        return ToolResponse(
            success=False,
            output="I couldn't understand that setting. Try formats like 'genre fantasy', 'process outliner', or 'goal finish first draft by August'."
        )
    
    def _generate_profile_summary(self, profile: Dict[str, Any]) -> str:
        name = profile["personal_info"]["name"] or "Not set"
        
        domains = ", ".join(profile["creative_preferences"]["domains"]) if profile["creative_preferences"]["domains"] else "Not specified"
        genres = ", ".join(profile["creative_preferences"]["genres"]) if profile["creative_preferences"]["genres"] else "Not specified"
        process = profile["creative_preferences"]["creative_process"] or "Not specified"
        
        short_goals = "\n  • " + "\n  • ".join(profile["creative_goals"]["short_term"]) if profile["creative_goals"]["short_term"] else "None set"
        challenges = "\n  • " + "\n  • ".join(profile["creative_goals"]["challenges"]) if profile["creative_goals"]["challenges"] else "None set"
        
        coaching_sessions = profile["stats"]["coaching_sessions"]
        projects = profile["stats"]["projects_completed"]
        
        summary = f"""**Your Creative Coach Profile**

**Creator:** {name}

**Creative Preferences:**
• Creative Domains: {domains}
• Preferred Genres: {genres}
• Creative Process: {process}

**Creative Goals:**
• Short-term Goals: {short_goals}
• Creative Challenges: {challenges}

**Activity:**
• Coaching Sessions: {coaching_sessions}
• Completed Projects: {projects}

Update your profile with commands like:
'/profile set genre fantasy' or '/profile set process outliner'
"""
        return summary
    
    def _get_user_profile(self, user_id: str) -> dict:
        """Return the user's profile dict, creating it if it doesn't exist."""
        if user_id not in self.user_profiles:
            self.user_profiles[user_id] = self._create_initial_profile()
        return self.user_profiles[user_id]


# For testing this agent in isolation
if __name__ == "__main__":
    # Example usage
    from multi_tool_agent.models.schemas import ToolRequest
    
    agent = ProfileAgent()
    
    # Test profile command
    request = ToolRequest(input="/profile view", user_id="test_user")
    response = agent.process(request)
    print(f"Profile view response:\n{response.output}")
    
    # Test different creative coaching approaches
    print("\nTesting different creative coaching approaches:")
    context = {"genre": "fantasy", "mood": "mysterious", "topic": "a hero's journey"}
    
    for _ in range(3):  # Test multiple responses to show variety
        request = ToolRequest(
            input="",
            user_id="test_user",
            context={"advice": True, "context": "story_creation", "genre": "fantasy", "mood": "mysterious"}
        )
        response = agent.process(request)
        print(f"\nCreative coaching:\n{response.output}")