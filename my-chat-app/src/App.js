import React, { useState } from "react";
import { BrowserRouter as Router, Routes, Route, useNavigate } from "react-router-dom";
import ChatApp from "./components/ChatApp";
import StoryCreator from "./components/StoryCreator";
import RandomStory from "./components/RandomStory";
import ProfilePage from "./components/ProfilePage"; 
import NavBar from "./components/NavBar";
import ErrorBoundary from "./ErrorBoundary";
import { fetchAPI } from './utils/api';
import "./App.css";

// This component needs to be inside Router to use navigation hooks
const AppContent = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [messages, setMessages] = useState([]);
  const navigate = useNavigate();
  
  const highlightCreateButton = () => {
    const createButton = document.querySelector('.nav-button');
    if (createButton) {
      createButton.classList.add('highlight-button');
      
      setTimeout(() => {
        createButton.classList.remove('highlight-button');
      }, 3000);
    }
  };

  const handleAgentResponse = (response) => {
    if (response && (response.message === "REDIRECT_TO_STORY_CREATOR" || 
        response.message === "REDIRECT_TO_STORY_CREATOR_FORCE")) {
      
      setMessages(prev => [...prev, {
        id: Date.now(),
        text: response.output,
        sender: 'bot'
      }]);
      
      highlightCreateButton();
      
      setTimeout(() => {
        navigate('/create');
      }, 2000);
      
      return;
    }
    
    setMessages(prev => [...prev, {
      id: Date.now(),
      text: response.output || "I couldn't process that request.",
      sender: 'bot'
    }]);
  };

  const handleSendMessage = async (message) => {
    setIsLoading(true);

    setMessages(prev => [...prev, {
      id: Date.now(),
      text: message,
      sender: 'user'
    }]);

    try {
      const data = await fetchAPI('/api/chat', {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          input: message,
          user_id: "anonymous_user",
          hour: new Date().getHours(), // <-- add this if needed
        }),
      });
      setIsLoading(false);
      handleAgentResponse(data);

      return data.output;
    } catch (error) {
      console.error("Error sending message:", error);
      setIsLoading(false);

      setMessages(prev => [...prev, {
        id: Date.now(),
        text: "Sorry, there was an error processing your request.",
        sender: 'bot'
      }]);

      return "Sorry, there was an error processing your request.";
    }
  };

  const handleCreateStory = (storyText) => {
    if (storyText) {
      setMessages(prev => [...prev, {
        id: Date.now(),
        text: "Here's your generated story:\n\n" + storyText,
        sender: 'bot'
      }]);
    }
  };

  return (
    <div className="app-container">
      <NavBar /> {/* This should be the ONLY instance */}
      <div className="content-container">
        <Routes>
          <Route path="/" element={
            <ChatApp 
              onSendMessage={handleSendMessage}
              isLoading={isLoading}
              messages={messages}
              setMessages={setMessages}
            />
          } />
          <Route path="/create" element={
            <StoryCreator 
              onCreateStory={handleCreateStory}
              onBackToChat={() => navigate('/')} 
            />
          } />
          <Route path="/random-story" element={
            <RandomStory />
          } />
          <Route path="/profile" element={<ProfilePage />} />
          {/* Add fallback for unknown routes */}
          <Route path="*" element={
            <div className="not-found">
              <h2>Page Not Found</h2>
              <p>The page you requested does not exist.</p>
              <button onClick={() => navigate('/')}>Go Home</button>
            </div>
          } />
        </Routes>
      </div>
    </div>
  );
};

function App() {
  return (
    <Router future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
      <ErrorBoundary>
        <AppContent />
      </ErrorBoundary>
    </Router>
  );
}

export default App;

// Make sure your API endpoint includes the message field in the JSON response
// (Remove Python code from this JavaScript file)
