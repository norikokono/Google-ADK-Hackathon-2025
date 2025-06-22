import React, { useState, useRef, useEffect } from "react";
import ReactMarkdown from 'react-markdown';
import StoryCreator from '../components/StoryCreator';
import { fetchAPI } from '../utils/api';
import './ChatApp.css';

const ChatApp = () => {
  const [currentView, setCurrentView] = useState('chat');
  const [isFirstLoad, setIsFirstLoad] = useState(true);
  const [isLoading, setIsLoading] = useState(false);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const messagesEndRef = useRef(null);

  // Scroll to latest message
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // Show the help message once we have the greeting
  useEffect(() => {
    if (isFirstLoad && messages.length === 1) {
      console.log("Showing welcome help message");
      const welcomeTimeout = setTimeout(() => {
        setMessages(prev => [...prev, {
          id: Date.now(),
          sender: 'bot',
          text: `🚀 Welcome to PlotBuddy Help!\n\n`
        }]);
        setIsFirstLoad(false);
      }, 1000);

      return () => clearTimeout(welcomeTimeout);
    }
  }, [messages.length, isFirstLoad]);

  // Only fetch greeting on first load and when no messages exist
  useEffect(() => {
    if (isFirstLoad && messages.length === 0) {
      const fetchInitialGreeting = async () => {
        try {
          console.log("Fetching initial greeting...");
          const data = await fetchAPI('/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              input: "hi",
              user_id: "anonymous_user"
            })
          });

          console.log("Initial greeting:", data);

          if (data.output || data.message) {
            setMessages([{
              id: Date.now(),
              sender: 'bot',
              text: data.output || data.message
            }]);
          }
        } catch (error) {
          console.error('Error fetching greeting:', error);
        }
      };

      fetchInitialGreeting();
    }
  }, [isFirstLoad, messages.length]);

  // Handles sending messages
  const handleSendMessage = async (message) => {
    try {
      if (!message || message.trim() === '') {
        console.log("Empty message, not sending");
        return;
      }

      setIsLoading(true);

      // Add user message immediately
      setMessages(prev => [...prev, {
        id: Date.now(),
        sender: 'user',
        text: message
      }]);

      // Send request to backend
      const data = await fetchAPI('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          input: message,
          user_id: "anonymous_user"
        })
      });

      console.log("API response:", data);

      // Check for redirection flags with better logging
      if (data.message === "REDIRECT_TO_STORY_CREATOR" ||
        data.message === "REDIRECT_TO_STORY_CREATOR_FORCE") {

        console.log("🔄 REDIRECT flag detected in response");

        // Add the bot response to chat
        setMessages(prev => [...prev, {
          id: Date.now() + 1,
          sender: 'bot',
          text: data.output || "Great! Let's create your story."
        }]);

        // Force immediate redirect for FORCE flag, or small delay for regular flag
        const delay = data.message === "REDIRECT_TO_STORY_CREATOR_FORCE" ? 500 : 1000;

        console.log(`⏳ Scheduling redirect in ${delay}ms`);

        // Set a timeout for the redirect to allow user to read the message
        setTimeout(() => {
          console.log(`⏰ Executing redirect now (${data.message})...`);
          setCurrentView('create');
        }, delay);

        setIsLoading(false);
        setInput('');
        return; // Exit early after setting up redirect
      }

      // Normal response
      setMessages(prev => [...prev, {
        id: Date.now() + 1,
        sender: 'bot',
        text: data.output || data.message || "Sorry, I couldn't process that."
      }]);

      setIsLoading(false);
      setInput('');
    } catch (error) {
      console.error('Error sending message:', error);

      // Show error to user
      setMessages(prev => [...prev, {
        id: Date.now() + 1,
        sender: 'bot',
        text: "Sorry, there was an error processing your message."
      }]);

      setIsLoading(false);
    }
  };

  const handleStoryCreated = (storyResultText) => {
    setMessages(msgs => [
      ...msgs,
      {
        id: Date.now(),
        sender: "bot",
        text: "✨ Here's your generated story:"
      },
      {
        id: Date.now() + 1,
        sender: "bot",
        text: storyResultText
      }
    ]);

    setCurrentView('chat');
  };

  // Only ONE return statement per component
  return (
    <div className="chat-app">
      {/* Floating logo component */}
      <img src="/assets/images/plotbuddy-text-logo.svg" alt="PlotBuddy" className="floating-logo" />

      {currentView === 'chat' ? (
        <div className="chat-container">
          <header className="chat-header">
            <h1 style={{
              textAlign: 'center',
              marginBottom: '10px'
            }}>Plot<span>Buddy</span></h1>

            <h2 style={{
              textAlign: 'center',
              marginTop: '0',
              marginBottom: '20px'
            }}>AI Writing Assistant</h2>
          </header>

          {/* Center welcome content but keep help items left-aligned */}
          <div className="welcome-help" style={{ textAlign: 'center' }}>
            <h3>🚀 Welcome to PlotBuddy Help!</h3>
            <p>Here's how I can help you today:</p>

            <h4>--- General Commands ---</h4>
            <div className="help-items" style={{
              display: 'inline-block',
              textAlign: 'left',
              maxWidth: '600px'
            }}>
              <p>Type <code>help</code> to see this message again.</p>
              <p>Ask <code>how it works</code> to understand my creative process.</p>
              <p>Say <code>contact support</code> for help or feedback.</p>
            </div>

            <h4>--- Story Creation ---</h4>
            <div className="help-items" style={{
              display: 'inline-block',
              textAlign: 'left',
              maxWidth: '600px'
            }}>
              <p>Ask <code>what genres</code> are available to get inspired.</p>
              <p>To start a story, tell me <code>create story</code> or <code>write a story</code>.</p>
            </div>

            <h4>--- Account & Pricing ---</h4>
            <div className="help-items" style={{
              display: 'inline-block',
              textAlign: 'left',
              maxWidth: '600px'
            }}>
              <p>Ask <code>what are your prices</code> or <code>subscription plans</code>.</p>
              <p>Query <code>business hours</code> for support availability.</p>
            </div>

            <p>I'm here to bring your ideas to life!</p>
          </div>

          {/* Then show messages */}
          <div className="messages">
            {messages.map((msg) => (
              <div key={msg.id} className={`message message-${msg.sender}`}>
                {msg.type === 'html' ? (
                  <div dangerouslySetInnerHTML={{ __html: msg.html }} />
                ) : (
                  <ReactMarkdown>{msg.text}</ReactMarkdown>
                )}
              </div>
            ))}
            <div ref={messagesEndRef} />
          </div>

          <div className="chat-input">
            <input
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={e => {
                if (e.key === 'Enter') handleSendMessage(input);
              }}
              placeholder="Type your message..."
              autoFocus
              disabled={isLoading}
            />
            <button
              className="send-button"
              onClick={() => handleSendMessage(input)}
              disabled={isLoading}
            >
              {isLoading ? "Sending..." : "Send"}
            </button>
          </div>
        </div>
      ) : (
        <StoryCreator
          onCreateStory={handleStoryCreated}
          onBackToChat={() => setCurrentView('chat')}
          isLoading={false}
        />
      )}
    </div>
  );
};

export default ChatApp;