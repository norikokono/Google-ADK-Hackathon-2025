# 🌟 PlotBuddy: AI-Powered Story Creation Assistant 🌟

## 🏆 Google Cloud ADK Hackathon Submission 2025 🏆

[PlotBuddy Logo](my-chat-app/public/assets/images/plotbuddy-logo.svg)
[PlotBuddy Logo](my-chat-app/public/assets/images/plotbuddy-text-logo.svg)

---

## 📝 Project Summary 📝

PlotBuddy is an AI-powered multi-agent system designed to assist writers in developing stories through intelligent conversation. ✨ Created for the Google Cloud Agent Development Kit Hackathon 2025, PlotBuddy leverages specialized AI agents to provide personalized creative assistance, answer questions, and guide users through the storytelling process. 🚀

---

## ✨ Features & Functionality ✨

### 🤖 Multi-Agent Architecture 🤖

* **🧠 Manager Agent (Gemini 2.0):** Coordinates between specialized agents, routes user requests, and ensures seamless transitions
* **👋 Greeting Agent:** Welcomes users and provides initial guidance
* **📚 Story Agent:** Specializes in narrative creation with varying lengths and styles
* **❓ FAQ Agent:** Answers questions about using the application
* **👤 Profile Agent:** Provides personalized creative coaching

### 📖 Story Creation 📖

Four standardized story lengths with reading time estimates:

* **🐣 Micro:** ~100 words (2-3 min read)
* **🐤 Short:** ~500 words (5-7 min read)
* **🦅 Medium:** ~1000 words (10-12 min read)
* **🦢 Long:** ~2000 words (15-20 min read)
* 🎭 Genre, mood, and style selection to personalize story creation
* 💡 Story brainstorming and editing capabilities

### 🎯 User Experience 🎯

* 💬 Intuitive chat interface for natural interaction
* ✏️ Dedicated story creation environment
* 🔄 Smooth transitions between different agent specialties
* ✨ Animated visual elements for engaging experience

---

## 🛠️ Technologies Used 🛠️

### 💻 Core Technologies 💻

* **🤖 Google Agent Development Kit (ADK):** Foundation for building the multi-agent system
* **🧠 Google Gemini AI Models:**
    * 🚀 Gemini 2.0 Pro: Powers the Manager Agent for intelligent request routing
    * ⚡ Gemini 1.5 Flash: Powers specialized agents for efficient responses
* **🐍 Python:** Backend service with FastAPI
* **⚛️ React:** Frontend user interface
* **🎨 CSS3:** Animations and responsive design

### 🔧 Development Tools 🔧

* **💻 VS Code:** Primary development environment
* **📊 Git:** Version control
* **📦 npm:** Package management for frontend
* **📦 pip:** Package management for backend

---

## 🏗️ Architecture Diagram 🏗️

[Include Architecture Diagram showing how components interact]

The architecture follows a hub-and-spoke model where the **Manager Agent** serves as the central coordinator that routes user requests to specialized agents:

1.  **👤 User** requests come through the React frontend
2.  **🌐 Backend API** processes requests and forwards to the **Manager Agent**
3.  **🧠 Manager Agent** analyzes intent and routes to appropriate specialized agent
4.  **🤖 Specialized agent** generates response
5.  **↩️ Response** returns through the API to the frontend
6.  **😃 User** receives personalized assistance

### 📚 Other Data Sources 📚

* 📜 **Narrative Structures:** Incorporated classic storytelling frameworks (three-act structure, hero's journey) for guiding story generation
* 🎭 **Genre Conventions:** Included typical elements and tropes of various genres to enhance story quality
* ✍️ **Writing Best Practices:** Implemented guidance based on established writing techniques for different story lengths

---

## 🔍 Findings & Learnings 🔍

### 💡 Technical Insights 💡

* **🧩 Effective Agent Specialization:** Dividing responsibilities between specialized agents led to more coherent and contextually appropriate responses
* **🎯 Intent Classification Challenges:** Accurately determining user intent required multiple iterations to prevent misrouting requests
* **✨ Prompt Engineering Importance:** Carefully crafted prompts were critical for generating appropriate responses, especially for story creation
* **🧠 Context Management:** Maintaining conversation context across agent transitions proved crucial for a seamless user experience

### 👥 User Experience Discoveries 👥

* **⚖️ Balance of Guidance vs. Freedom:** Users appreciated both structured guidance and creative freedom in story development
* **🌉 Importance of Transitions:** Smooth transitions between agents significantly improved perceived continuity of assistance
* **📏 Story Length Preferences:** Users gravitated toward shorter formats initially but expanded to longer formats as they became comfortable

### 🚧 Development Challenges 🚧

* **🔄 Agent Coordination:** Managing the flow of information between agents required careful design
* **🛠️ Error Handling:** Developing robust error recovery without disrupting the user experience
* **⚡ Performance Optimization:** Balancing response quality with response time, particularly for longer story generation

---

## 🚀 Installation & Setup 🚀

1.  **Clone the repository**
2.  **Install dependencies**
3.  **Set up environment variables**
4.  **Run the application**
5.  **Access PlotBuddy**
    * Open your browser and go to `http://localhost:3000`
    * Start creating stories with the help of PlotBuddy's AI agents!

---

## 📖 Usage Guide 📖

### 🤖 Interacting with Agents 🤖

* **Manager Agent:** The central point for all interactions. Asks clarifying questions and routes to specialized agents.
* **Greeting Agent:** Initiates conversation, gathers initial user preferences.
* **Story Agent:** Engages in detailed story development, from brainstorming to editing.
* **FAQ Agent:** Provides assistance on using the application, answering common questions.
* **Profile Agent:** Offers personalized tips and guidance based on user profile.

---

## 🛠️ Troubleshooting Tips 🛠️

If you encounter issues, try the following:

* Refresh the browser page
* Check the terminal for error messages
* Ensure all services are running (backend and frontend)
* Review the configuration in the `.env` file
* Consult the documentation for common troubleshooting steps

---

## 📅 Future Enhancements 📅

* **🌐 Expanded Agent Capabilities:** Introduce new agents for additional writing-related tasks (e.g., research, outlining)
* **📊 Analytics Dashboard:** Provide users with insights into their writing patterns and progress
* **📚 Resource Library:** Curate a collection of writing resources, templates, and guides
* **🤝 Collaboration Features:** Enable multiple users to collaborate on stories in real-time
* **📱 Mobile Application:** Extend PlotBuddy's functionality to mobile devices for on-the-go writing assistance

---

## 🙏 Acknowledgments 🙏

* **Google Cloud:** For providing the Agent Development Kit and supporting innovative projects
* **OpenAI:** For the powerful language models that enable intelligent agent responses
* **GitHub:** For hosting the repository and facilitating collaboration
* **All Contributors:** For their hard work, creativity, and dedication to making PlotBuddy a reality

---

## 📜 License 📜

This project is licensed under the MIT License - see the `LICENSE` file for details.

---

Thank you for considering PlotBuddy for your story creation needs! We believe our AI-powered assistant can significantly enhance your writing process, making it more enjoyable and productive. We look forward to your feedback and hope you join us on this exciting journey of storytelling innovation!