import React, { useState, useRef, useEffect } from 'react';
import PropTypes from 'prop-types';
import './ChatWindow.css';
import { fetchAPI } from '../utils/api';


const ChatWindow = ({ onSendMessage, isLoading }) => {
  const [message, setMessage] = useState('');
  const [messages, setMessages] = useState([]);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!message.trim() || isLoading) return;

    // Add user message
    const userMessage = {
      id: Date.now(),
      text: message,
      sender: 'user'
    };
    
    // Add to messages state
    setMessages(prevMessages => [...prevMessages, userMessage]);
    
    // Save message before clearing input
    const currentMessage = message;
    
    // Clear input field
    setMessage('');
    
    try {
      // Call the onSendMessage prop with the message
      const response = await onSendMessage(currentMessage);
      
      // Add bot response to messages
      if (response) {
        const botMessage = {
          id: Date.now() + 1,
          text: response,
          sender: 'bot'
        };
        
        setMessages(prevMessages => [...prevMessages, botMessage]);
      }
    } catch (error) {
      console.error('Error sending message:', error);
      
      // Add error message
      const errorMessage = {
        id: Date.now() + 1,
        text: 'Sorry, there was an error processing your message.',
        sender: 'bot',
        error: true
      };
      
      setMessages(prevMessages => [...prevMessages, errorMessage]);
    }
  };

  const handleRandomStory = async () => {
    try {
      console.log("Calling API at /api/story/create");
      const data = await fetchAPI('/api/story/create', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ /* your request payload */ }),
      });

      // handle success, e.g., update messages with the new story
      // handle success, e.g., update messages with the new story
    } catch (err) {
      console.error("Full error details:", err);
      // handle error, e.g., show error message in the chat
    }
  };

  return (
    <div className="chat-window">
      <div className="chat-messages">
        {messages.map(msg => (
          <div key={msg.id} className={`chat-message ${msg.sender}`}>
            <div className="message-content">
              {msg.text}
            </div>
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>
      <form onSubmit={handleSubmit} className="chat-input-form">
        <input
          type="text"
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          placeholder="Type your message..."
          disabled={isLoading}
        />
        <button type="submit" disabled={isLoading}>
          {isLoading ? 'Sending...' : 'Send'}
        </button>
      </form>
    </div>
  );
};

ChatWindow.propTypes = {
  onSendMessage: PropTypes.func.isRequired,
  isLoading: PropTypes.bool
};

ChatWindow.defaultProps = {
  isLoading: false
};

export default ChatWindow;