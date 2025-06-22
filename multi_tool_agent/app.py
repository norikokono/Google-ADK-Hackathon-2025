from google.cloud.ai.generativelanguage.adk import agent_app
from multi_tool_agent.adk_compatibility import agent, tool, init_adk_compatibility
import logging
import os

init_adk_compatibility()  # Register all tools

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Create the ADK agent application
app = agent_app.AgentApp(
    name="plotbuddy",
    manifest_path="./manifest.yaml",
    agent_module_paths=[
        "multi_tool_agent.agents.orchestrator",  # Orchestrator (was manager)
        "multi_tool_agent.agents.story",         # Story agent
        "multi_tool_agent.agents.faq",           # FAQ agent
        "multi_tool_agent.agents.profile",       # Profile agent
        "multi_tool_agent.agents.greeting"       # Greeting agent
    ]
)

# Add any middleware or additional configuration here
print("GOOGLE_API_KEY:", os.environ.get("GOOGLE_API_KEY"))
if __name__ == "__main__":
    # Get port from environment or default to 8080
    port = int(os.environ.get("PORT", 8080))
    
    # Run the application
    app.run(host="0.0.0.0", port=port)