import React, { useState, useEffect } from 'react';
import PropTypes from 'prop-types';
import StoryGuide from './StoryGuide';
import './StoryCreator.css';


const StoryCreator = ({ onCreateStory, onBackToChat }) => {
  const [storyConfig, setStoryConfig] = useState({
    genre: '',
    mood: '',
    length: ''
  });
  const [generatedStoryText, setGeneratedStoryText] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [showGuide, setShowGuide] = useState(true);
  const [profileAgentMessage, setProfileAgentMessage] = useState('');
  const [showSpeechBubble, setShowSpeechBubble] = useState(true);

  const genres = [
    { value: 'mystery', label: 'Mystery - Detective stories and puzzles' },
    { value: 'scifi', label: 'Sci-Fi - Future and technology' },
    { value: 'fantasy', label: 'Fantasy - Magic and wonder' },
    { value: 'romance', label: 'Romance - Love and relationships' },
    { value: 'adventure', label: 'Adventure - Journeys and quests' },
    { value: 'horror', label: 'Horror - Suspense and fear' },
    { value: 'comedy', label: 'Comedy - Humor and lightheartedness' },
    { value: 'thriller', label: 'Thriller - Intense suspense and plot twists' },
    { value: 'historical', label: 'Historical - Past events and periods' },
    { value: 'western', label: 'Western - Frontier and cowboys' },
    { value: 'cyberpunk', label: 'Cyberpunk - Dystopian tech future' }
  ];

  const moods = [
    { value: 'mysterious', label: 'Mysterious - Intriguing and suspenseful' },
    { value: 'whimsical', label: 'Whimsical - Light and playful' },
    { value: 'dark', label: 'Dark - Serious and moody' },
    { value: 'romantic', label: 'Romantic - Warm and emotional' },
    { value: 'epic', label: 'Epic - Grand and inspiring' },
    { value: 'funny', label: 'Funny - Humorous and amusing' },
    { value: 'melancholic', label: 'Melancholic - Sad and thoughtful' },
    { value: 'suspenseful', label: 'Suspenseful - Tense and exciting' },
    { value: 'nostalgic', label: 'Nostalgic - Longing for the past' },
    { value: 'dreamy', label: 'Dreamy - Visionary and ethereal' },
    { value: 'tense', label: 'Tense - Stressful and strained' },
    { value: 'peaceful', label: 'Peaceful - Calm and tranquil' },
    { value: 'chaotic', label: 'Chaotic - Disordered and turbulent' }
  ];

  const lengths = [
    { value: 'micro', label: 'Micro - ~100 words (2-3 min)' },
    { value: 'short', label: 'Short - ~500 words (5-7 min)' },
    { value: 'medium', label: 'Medium - ~1000 words (10-12 min)' },
    { value: 'long', label: 'Long - ~2000 words (15-20 min)' }
  ];

  const handleChange = (e) => {
    const { name, value } = e.target;
    setStoryConfig(prev => ({
      ...prev,
      [name]: value
    }));
  };

  // Function to create a story
  const createStory = async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await fetch('/api/story/create', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: 'anonymous_user',
          genre: storyConfig.genre,
          mood: storyConfig.mood,
          length: storyConfig.length
        })
      });
      
      const data = await response.json();
      console.log("Story API response:", data);
      
      if (data.success) {
        // Fix: Use data.story instead of data.message
        setGeneratedStoryText(data.story || data.output || data.message);
      } else {
        setError(data.message || 'Failed to generate story');
      }
    } catch (err) {
      console.error("Story creation error:", err);
      setError('An error occurred while creating your story.');
    } finally {
      setIsLoading(false);
    }
  };

  // Add a separate function for when user wants to go back to chat
  const handleBackToChat = () => {
    if (generatedStoryText) {
      // Only pass the story back when explicitly going back to chat
      onCreateStory(generatedStoryText);
    }
    onBackToChat();
  };

  // Function to handle downloading the generated story
  const handleDownloadStory = () => {
    if (!generatedStoryText || !isSuccessStory(generatedStoryText)) {
      alert("No valid story to download.");
      return;
    }

    const element = document.createElement("a");
    const sanitizeFilename = (str) => str ? str.replace(/[^a-z0-9_.-]/gi, '_').toLowerCase() : 'untitled';
    const filename = `${sanitizeFilename(storyConfig.genre)}_${sanitizeFilename(storyConfig.mood)}_${sanitizeFilename(storyConfig.length)}.txt`;

    const file = new Blob([generatedStoryText], {type: 'text/plain;charset=utf-8'});
    element.href = URL.createObjectURL(file);
    element.download = filename;
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
    URL.revokeObjectURL(element.href);
  };

  // Helper to determine if the generated text is a successful story or an error
  const isSuccessStory = (text) => {
    return text && !text.startsWith("Error:") && !text.startsWith("Sorry,") && !text.startsWith("⚠️");
  };

  const isFormValid = storyConfig.genre && storyConfig.mood && storyConfig.length;

  const getLabelPart = (value, optionsArray) => {
    const foundOption = optionsArray.find(opt => opt.value === value);
    return foundOption ? foundOption.label.split(' - ')[0] : 'N/A';
  };

  const handleSubmit = (e) => {
    e.preventDefault();    
    
    createStory();
  };

  // Debug log when story text changes
  useEffect(() => {
    if (generatedStoryText) {
      console.log("Story text set:", generatedStoryText.substring(0, 50) + "...");
    }
  }, [generatedStoryText]);

  // Add this function to your component
  const createRipple = (event) => {
    const button = event.currentTarget;
    
    // Remove any existing ripple elements
    const ripple = button.getElementsByClassName("ripple")[0];
    if (ripple) {
      ripple.remove();
    }
    
    // Create new ripple element
    const circle = document.createElement("span");
    const diameter = Math.max(button.clientWidth, button.clientHeight);
    
    circle.style.width = circle.style.height = `${diameter}px`;
    circle.style.left = `${event.clientX - button.getBoundingClientRect().left - diameter / 2}px`;
    circle.style.top = `${event.clientY - button.getBoundingClientRect().top - diameter / 2}px`;
    circle.classList.add("ripple");
    
    button.appendChild(circle);
  };

  // Function to fetch profile agent message
  const fetchProfileAgentMessage = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/profile/advice', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          context: 'story_creation',
          genre: storyConfig.genre,
          mood: storyConfig.mood
        })
      });
      
      const data = await response.json();
      if (data.success) {
        setProfileAgentMessage(data.output);
      }
    } catch (error) {
      console.error("Failed to fetch profile agent message:", error);
    }
  };

  // Function to request story brainstorming ideas
  const requestBrainstorming = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/profile/brainstorm', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          genre: storyConfig.genre,
          mood: storyConfig.mood,
          length: storyConfig.length
        })
      });
      
      const data = await response.json();
      if (data.success) {
        setProfileAgentMessage(data.output);
      }
    } catch (error) {
      console.error("Failed to start brainstorming:", error);
    }
  };

  // Toggle the visibility of the speech bubble
  const toggleSpeechBubble = () => {
    setShowSpeechBubble(!showSpeechBubble);
  };

  // Fetch profile agent message when form values change
  useEffect(() => {
    if (showSpeechBubble) {
      fetchProfileAgentMessage();
    }
  }, [storyConfig.genre, storyConfig.mood, storyConfig.length, showSpeechBubble]);

  return (
    <div className="story-creator">
      {/* Creator header buttons */}
      <div className="creator-header">
        <h1>Story Creator</h1>
        <div className="header-buttons">
          <button 
            onClick={(e) => {
              createRipple(e);
              setShowGuide(!showGuide);
            }} 
            className="btn btn-toggle"
          >
            {showGuide ? 'Hide Guide' : 'Show Guide'}
          </button>
          <button 
            onClick={(e) => {
              createRipple(e);
              onBackToChat();
            }} 
            className="btn btn-secondary"
          >
            Back to Chat
          </button>
        </div>
      </div>

      {/* Profile agent bubble - Welcome message and actions */}
      {showSpeechBubble && (
        <div className="profile-agent-bubble">
          <div className="profile-agent-avatar">
            <img src="../assets/images/plotbuddy-logo.svg" alt="PlotBuddy logo" />
          </div>
          <div className="speech-bubble">
            <p>
              {profileAgentMessage || (
                <span>
                  Welcome to PlotBuddy Story Creator! 
                  What kind of story would you like to create today? I'm here to help with ideas and suggestions.
                </span>
              )}
            </p>
            <div className="speech-actions">
              <button className="speech-action-btn" onClick={requestBrainstorming}>
                <i className="fa fa-lightbulb-o"></i> PlotBuddy Support 💗
              </button>
              <button className="speech-action-btn" onClick={toggleSpeechBubble}>
                <i className="fa fa-times"></i>Close ❎
              </button>
            </div>
          </div>
        </div>
      )}
      
      <div className="creator-content">
        {showGuide && (
          <div className="guide-container">
            <StoryGuide />
          </div>
        )}
        
        <div className="story-form">
          <header className="creator-header" style={{ marginBottom: '30px' }}>
            <h1 style={{
              fontSize: '2.5em',
              color: '#1d9692',
              marginTop: '36px',
              marginBottom: '10px',
              fontWeight: '700'
            }}>
              Create Your Story
            </h1>
            <p style={{
              fontSize: '1.1em',
              color: '#555',
              lineHeight: '1.5'
            }}>
              Choose your story settings below and let the magic happen!
            </p>
          </header>

          <form onSubmit={handleSubmit} className="creator-form" style={{
            display: 'flex',
            flexDirection: 'column',
            gap: '20px'
          }}>
            <div className="form-group" style={{ textAlign: 'left' }}>
              <label htmlFor="genre" style={{
                display: 'block',
                marginBottom: '8px',
                fontWeight: '600',
                color: '#444'
              }}>
                Genre
              </label>
              <select
                id="genre"
                name="genre"
                value={storyConfig.genre}
                onChange={handleChange}
                disabled={isLoading}
                required
                style={{
                  width: '100%',
                  padding: '12px',
                  borderRadius: '8px',
                  border: '1px solid #ddd',
                  fontSize: '1em',
                  backgroundColor: '#f9f9f9',
                  boxShadow: 'inset 0 1px 3px rgba(0, 0, 0, 0.05)',
                  appearance: 'none',
                  backgroundImage: `url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='24' height='24' viewBox='0 0 24 24'%3E%3Cpath fill='none' stroke='%23444' stroke-linecap='round' stroke-linejoin='round' stroke-width='2' d='M6 9l6 6 6-6'/%3E%3C/svg%3E")`,
                  backgroundRepeat: 'no-repeat',
                  backgroundPosition: 'right 12px center',
                  backgroundSize: '24px'
                }}
              >
                <option value="">Select a genre</option>
                {genres.map(genre => (
                  <option key={genre.value} value={genre.value}>
                    {genre.label}
                  </option>
                ))}
              </select>
            </div>

            <div className="form-group" style={{ textAlign: 'left' }}>
              <label htmlFor="mood" style={{
                display: 'block',
                marginBottom: '8px',
                fontWeight: '600',
                color: '#444'
              }}>
                Mood
              </label>
              <select
                id="mood"
                name="mood"
                value={storyConfig.mood}
                onChange={handleChange}
                disabled={isLoading}
                required
                style={{
                  width: '100%',
                  padding: '12px',
                  borderRadius: '8px',
                  border: '1px solid #ddd',
                  fontSize: '1em',
                  backgroundColor: '#f9f9f9',
                  boxShadow: 'inset 0 1px 3px rgba(0, 0, 0, 0.05)',
                  appearance: 'none',
                  backgroundImage: `url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='24' height='24' viewBox='0 0 24 24'%3E%3Cpath fill='none' stroke='%23444' stroke-linecap='round' stroke-linejoin='round' stroke-width='2' d='M6 9l6 6 6-6'/%3E%3C/svg%3E")`,
                  backgroundRepeat: 'no-repeat',
                  backgroundPosition: 'right 12px center',
                  backgroundSize: '24px'
                }}
              >
                <option value="">Select a mood</option>
                {moods.map(mood => (
                  <option key={mood.value} value={mood.value}>
                    {mood.label}
                  </option>
                ))}
              </select>
            </div>

            <div className="form-group" style={{ textAlign: 'left' }}>
              <label htmlFor="length" style={{
                display: 'block',
                marginBottom: '8px',
                fontWeight: '600',
                color: '#444'
              }}>
                Length
              </label>
              <select
                id="length"
                name="length"
                value={storyConfig.length}
                onChange={handleChange}
                disabled={isLoading}
                required
                style={{
                  width: '100%',
                  padding: '12px',
                  borderRadius: '8px',
                  border: '1px solid #ddd',
                  fontSize: '1em',
                  backgroundColor: '#f9f9f9',
                  boxShadow: 'inset 0 1px 3px rgba(0, 0, 0, 0.05)',
                  appearance: 'none',
                  backgroundImage: `url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='24' height='24' viewBox='0 0 24 24'%3E%3Cpath fill='none' stroke='%23444' stroke-linecap='round' stroke-linejoin='round' stroke-width='2' d='M6 9l6 6 6-6'/%3E%3C/svg%3E")`,
                  backgroundRepeat: 'no-repeat',
                  backgroundPosition: 'right 12px center',
                  backgroundSize: '24px'
                }}
              >
                <option value="">Select a length</option>
                {lengths.map(length => (
                  <option key={length.value} value={length.value}>
                    {length.label}
                  </option>
                ))}
              </select>
            </div>

            {/* Create Story button */}
            <div className="form-buttons">
              <button
                type="submit"
                className="btn btn-primary"
                disabled={!isFormValid || isLoading}
                onClick={createRipple}
              >
                {isLoading ? (
                  <>
                    <span className="spinner"></span>
                    Creating Story...
                  </>
                ) : (
                  <>
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                      <path d="M12 5V19M5 12H19" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                    </svg>
                    Create Story
                  </>
                )}
              </button>

              {/* Back to Chat button */}
              <button
                type="button"
                className="btn btn-secondary"
                onClick={(e) => {
                  createRipple(e);
                  handleBackToChat();
                }}
                disabled={isLoading}
              >
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M19 12H5M5 12L12 19M5 12L12 5" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                </svg>
                Back to Chat
              </button>
            </div>
          </form>

          {isFormValid && !isLoading && !generatedStoryText && (
            <div className="preview-section" style={{
              marginTop: '30px',
              padding: '20px',
              backgroundColor: '#e6f7ff',
              borderRadius: '12px',
              border: '1px solid #91d5ff',
              textAlign: 'left'
            }}>
              <h2 style={{
                fontSize: '1.6em',
                color: '#0056b3',
                marginBottom: '15px'
              }}>
                Story Preview
              </h2>
              <p style={{ marginBottom: '8px', color: '#333' }}>
                <strong>Genre:</strong> {getLabelPart(storyConfig.genre, genres)}
              </p>
              <p style={{ marginBottom: '8px', color: '#333' }}>
                <strong>Mood:</strong> {getLabelPart(storyConfig.mood, moods)}
              </p>
              <p style={{ color: '#333' }}>
                <strong>Length:</strong> {getLabelPart(storyConfig.length, lengths)}
              </p>
            </div>
          )}

          {/* This section displays the generated story text on the same page */}
          {generatedStoryText && (
            <div className="generated-story-section" style={{
              marginTop: '30px',
              padding: '20px',
              backgroundColor: '#f9f9f9',
              borderRadius: '12px',
              boxShadow: '0 2px 10px rgba(0, 0, 0, 0.08)',
              textAlign: 'left'
            }}>
              {isSuccessStory(generatedStoryText) ? (
                <>
                  <h2 style={{
                    fontSize: '1.8em',
                    color: '#28a745',
                    marginBottom: '15px'
                  }}>
                    Generated Story
                  </h2>
                  <div className="story-content" style={{
                    whiteSpace: 'pre-wrap',
                    backgroundColor: '#ffffff',
                    padding: '15px',
                    borderRadius: '8px',
                    border: '1px solid #eee',
                    maxHeight: '400px',
                    overflowY: 'auto',
                    lineHeight: '1.6',
                    color: '#333'
                  }}>
                    {generatedStoryText}
                  </div>
                  <div className="story-actions" style={{
                    marginTop: '25px',
                    display: 'flex',
                    justifyContent: 'center'
                  }}>
                    {/* Download button for the generated story */}
                    <button
                      onClick={(e) => {
                        createRipple(e);
                        handleDownloadStory();
                      }}
                      className="btn btn-download"
                    >
                      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M12 4V16M12 16L7 11M12 16L17 11M6 20H18" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                      </svg>
                      Download Story
                    </button>
                  </div>
                </>
              ) : (
                <div className="story-error-message" style={{
                  backgroundColor: '#ffe0e0',
                  border: '1px solid #ff4d4d',
                  borderRadius: '12px',
                  padding: '20px'
                }}>
                  <h2 style={{
                    fontSize: '1.8em',
                    color: '#ff4d4d',
                    marginBottom: '15px'
                  }}>
                    Story Generation Failed
                  </h2>
                  <p style={{
                    whiteSpace: 'pre-wrap',
                    color: '#cc0000',
                    lineHeight: '1.6'
                  }}>
                    {generatedStoryText}
                  </p>
                </div>
              )}
            </div>
          )}
        </div>
      </div>

        {/* Remove the <style jsx> block; add keyframes to StoryCreator.css if needed */}
      </div>
  );
};

const FloatingLogo = () => {
  return <img src="../../public/assets/images/plotbuddy-logo.svg" alt="PlotBuddy" className="floating-logo" />;
};

StoryCreator.propTypes = {
  onCreateStory: PropTypes.func.isRequired,
  onBackToChat: PropTypes.func.isRequired
};

export default StoryCreator;
