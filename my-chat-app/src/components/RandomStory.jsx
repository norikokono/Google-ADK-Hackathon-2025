import React, { useState, useEffect } from 'react';
import PropTypes from 'prop-types';
import StoryGuide from './StoryGuide';
import './RandomStory.css';

const API_URL = 'http://localhost:8000'; // URL where your FastAPI server is running locally

const RandomStory = () => {
  const [generatedStoryText, setGeneratedStoryText] = useState('');
  const [storyConfig, setStoryConfig] = useState({
    genre: '',
    mood: '',
    length: ''
  });
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  // Lists of options for display purposes
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

  // Create ripple effect for buttons
  const createRipple = (event) => {
    const button = event.currentTarget;
    const ripple = button.getElementsByClassName("ripple")[0];
    
    if (ripple) {
      ripple.remove();
    }
    
    const circle = document.createElement("span");
    const diameter = Math.max(button.clientWidth, button.clientHeight);
    
    circle.style.width = circle.style.height = `${diameter}px`;
    circle.style.left = `${event.clientX - button.getBoundingClientRect().left - diameter / 2}px`;
    circle.style.top = `${event.clientY - button.getBoundingClientRect().top - diameter / 2}px`;
    circle.classList.add("ripple");
    
    button.appendChild(circle);
  };

  // Generate a random story function
  const handleRandomStory = async (e) => {
    if (e) createRipple(e);
    setIsLoading(true);
    setError(null);
    
    try {
      console.log("🎲 Generating random story...");
      
      // Add timeout in case server takes too long
      const timeoutPromise = new Promise((_, reject) => 
        setTimeout(() => reject(new Error("Request timeout after 15 seconds")), 15000)
      );
      
      const fetchPromise = fetch(`${API_URL}/api/story/create`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: 'anonymous_user',
          // Add more details to help debug the backend issue
          random: true,
          client_version: '1.0.1',
          timestamp: new Date().toISOString()
        })
      });
      
      // Race between fetch and timeout
      const response = await Promise.race([fetchPromise, timeoutPromise]);
      
      if (!response.ok) {
        // Better error handling for specific status codes
        if (response.status === 500) {
          throw new Error("Server error: The story generator is experiencing technical difficulties");
        } else {
          throw new Error(`Server returned ${response.status}: ${response.statusText}`);
        }
      }
      
      const data = await response.json();
      console.log("📄 Random story generated:", data);
      
      if (data.success) {
        // Set the generated story text
        setGeneratedStoryText(data.story || data.message);
        
        // Safely update parameters with null checks
        if (data.parameters) {
          setStoryConfig({
            genre: data.parameters.genre || '',
            mood: data.parameters.mood || '',
            length: data.parameters.length || ''
          });
        } else {
          // Fallback for missing parameters
          setStoryConfig({
            genre: 'mystery',
            mood: 'suspenseful',
            length: 'short'
          });
        }
        
        // Auto-scroll to the story section
        setTimeout(() => {
          const storySection = document.querySelector('.generated-story-section');
          if (storySection) {
            storySection.scrollIntoView({ behavior: 'smooth', block: 'start' });
          }
        }, 300);
      } else {
        setError(data.message || "Failed to generate random story");
      }
    } catch (err) {
      console.error("Error generating random story:", err);
      // More user-friendly error message
      setError(`Sorry, I couldn't create your story: ${err.message}. Please try again in a few moments.`);
      
      // Provide fallback story for better UX
      setGeneratedStoryText("Sorry, I couldn't generate your story right now. Our AI storyteller needs a short break. Please try again in a moment!");
    } finally {
      setIsLoading(false);
    }
  };

  // Function to handle downloading the generated story
  const handleDownloadStory = () => {
    if (!generatedStoryText || !isSuccessStory(generatedStoryText)) {
      alert("No valid story to download.");
      return;
    }

    const element = document.createElement("a");
    const sanitizeFilename = (str) => str ? str.replace(/[^a-z0-9_.-]/gi, '_').toLowerCase() : 'untitled';
    const filename = `random_story_${new Date().toISOString().substring(0, 10)}.txt`;

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

  const getLabelPart = (value, optionsArray) => {
    const foundOption = optionsArray.find(opt => opt.value === value);
    return foundOption ? foundOption.label.split(' - ')[0] : 'N/A';
  };

  return (
    <div className="examples-container" style={{
      maxWidth: '800px',
      margin: '0 auto',
      padding: '20px'
    }}>
      <header className="examples-header" style={{
        textAlign: 'center',
        marginBottom: '30px'
      }}>
        <h1
          style={{
            fontSize: '2.5em',
            background: 'linear-gradient(45deg,rgb(241, 248, 24),rgb(14, 70, 174))',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            marginBottom: '10px',
            textShadow: '1px 1px 3px rgba(198, 46, 181, 0.4)',
            transition: 'transform 0.3s ease'
          }}
          onMouseEnter={(e) => e.target.style.transform = 'scale(1.05)'}
          onMouseLeave={(e) => e.target.style.transform = 'scale(1)'}
        >
          Random Story Generator
        </h1>
        <p style={{
          fontSize: '1.2em',
          color: '#555',
          maxWidth: '600px',
          margin: '0 auto'
        }}>Generate random stories with a single click. Great for inspiration or just for fun!</p>
      </header>
      
      {/* Guide section with tips */}
      <div className="guide-section" style={{ 
        marginBottom: '40px', 
        padding: '20px', 
        borderRadius: '12px', 
        background: 'linear-gradient(to right,rgb(228, 253, 234),rgb(247, 230, 245))',
      }}>
        <h2 style={{ fontSize: '1.8em', color: '#444', marginBottom: '15px' }}>
          Story Creation Guide
        </h2>
        <p style={{ marginBottom: '15px', color: '#333' }}>
          Follow these pro tips to craft amazing stories. You can also generate a sample story based on these tips!
        </p>
        
        {/* Pro Tips section */}
        <section className="pro-tips">
          <h3 style={{ fontSize: '1.5em', color: '#00b3aa', marginBottom: '10px' }}>💡 Pro Tips</h3>
          <ul style={{ marginLeft: '20px', color: '#333', lineHeight: '1.6' }}>
            <li>Pair classic combinations: <strong>mystery + suspenseful</strong>, <strong>romance + dreamy</strong></li>
            <li>Try contrasts: <strong>cyberpunk + nostalgic</strong>, <strong>historical + whimsical</strong></li>
            <li>Start with micro stories (~100 words) to experiment with styles</li>
            <li>Match intensity: <strong>thriller + tense</strong>, <strong>fantasy + epic</strong></li>
            <li>Create atmosphere: <strong>horror + dark</strong>, <strong>western + peaceful</strong></li>
            <li>Mix timeframes: <strong>historical + chaotic</strong>, <strong>scifi + melancholic</strong></li>
          </ul>
        </section>
      </div>

      {/* Random story section */}
      <div className="random-story-section" style={{
        backgroundColor: '#f8f9fa',
        padding: '25px',
        borderRadius: '12px',
        boxShadow: '0 2px 10px rgba(0, 0, 0, 0.05)'
      }}>
        <h2 style={{
          fontSize: '1.8em',
          color: '#444',
          marginBottom: '15px',
          textAlign: 'center'
        }}>Generate a Random Story</h2>
         <div className="examples-info" style={{
          marginTop: '40px',
          padding: '20px',
          background: 'linear-gradient(to right,rgb(239, 249, 241),rgb(194, 246, 215),rgb(198, 239, 230))',
          borderRadius: '10px',
          border: '1px solidrgb(244, 163, 232)'
        }}>
          <h3 style={{
            fontSize: '1.4em',
            color: '#078587',
            marginBottom: '10px'
          }}>
            About Random Stories
          </h3>
          <p style={{
            color: '#333',
            lineHeight: '1.6'
          }}>
            Each time you click "Surprise Me!", our AI will select random story parameters and create a unique story. 
            This is a great way to discover unexpected combinations and spark your creativity.
          </p>
          <p style={{
            color: '#333',
            lineHeight: '1.6',
            marginTop: '10px'
          }}>
            If you prefer more control over your story creation, head over to the Story Creator where you can
            select specific genres, moods, and lengths for your stories.
          </p>
        </div>
        <p style={{
          fontSize: '1.1em',
          color: '#666',
          marginBottom: '20px',
          textAlign: 'center'
        }}>Click the button below to generate a completely random story with random genre, mood, and length.</p>
        
        <div className="surprise-button-container" style={{
          display: 'flex',
          justifyContent: 'center',
          marginBottom: '30px'
        }}>
          <button
            onClick={handleRandomStory}
            disabled={isLoading}
            className="btn-surprise"
            style={{
              fontSize: '1.2rem',
              padding: '16px 32px',
              background: 'linear-gradient(135deg, #FF9800, #FF5722)',
              color: 'white',
              border: 'none',
              borderRadius: '50px',
              cursor: 'pointer',
              boxShadow: '0 4px 15px rgba(255, 87, 34, 0.3)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '10px',
              transition: 'transform 0.3s ease, box-shadow 0.3s ease',
              position: 'relative',
              overflow: 'hidden'
            }}
          >
            {isLoading ? (
              <>
                <span className="spinner" style={{
                  display: 'inline-block',
                  width: '20px',
                  height: '20px',
                  border: '3px solid rgba(255,255,255,0.3)',
                  borderRadius: '50%',
                  borderTop: '3px solid white',
                  animation: 'spin 1s linear infinite'
                }}></span>
                Generating...
              </>
            ) : (
              <>
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M12 2l2 5h5l-4 4 2 6-5-3-5 3 2-6-4-4h5l2-5z" stroke="white" fill="white" strokeWidth="1" strokeLinecap="round" strokeLinejoin="round"/>
                </svg>
                Surprise Me! Generate Random Story
              </>
            )}
          </button>
        </div>
        
        {error && (
          <div className="error-message" style={{
            color: '#cc0000',
            padding: '15px',
            backgroundColor: '#ffe0e0',
            borderRadius: '8px',
            margin: '20px 0',
            textAlign: 'center'
          }}>
            <strong>Error:</strong> {error}
          </div>
        )}
        
        {/* Story display section */}
        {generatedStoryText && (
          <div className="generated-story-section" style={{
            marginTop: '30px',
            padding: '20px',
            backgroundColor: '#ffffff',
            borderRadius: '12px',
            boxShadow: '0 2px 10px rgba(0, 0, 0, 0.08)',
            textAlign: 'left'
          }}>
            {isSuccessStory(generatedStoryText) ? (
              <>
                <h2 style={{
                  fontSize: '1.8em',
                  color: '#28a745',
                  marginBottom: '15px',
                  textAlign: 'center'
                }}>Your Random Story</h2>
                
                <div className="story-parameters" style={{
                  display: 'flex',
                  justifyContent: 'center',
                  gap: '20px',
                  flexWrap: 'wrap',
                  marginBottom: '20px',
                  padding: '10px',
                  backgroundColor: '#f8f9fa',
                  borderRadius: '8px'
                }}>
                  <p><strong>Genre:</strong> {getLabelPart(storyConfig.genre, genres)}</p>
                  <p><strong>Mood:</strong> {getLabelPart(storyConfig.mood, moods)}</p>
                  <p><strong>Length:</strong> {getLabelPart(storyConfig.length, lengths)}</p>
                </div>
                
                <div className="story-content" style={{
                  whiteSpace: 'pre-wrap',
                  backgroundColor: '#ffffff',
                  padding: '20px',
                  borderRadius: '8px',
                  border: '1px solid #eee',
                  maxHeight: '400px',
                  overflowY: 'auto',
                  lineHeight: '1.6',
                  color: '#333',
                  fontSize: '1.1em'
                }}>
                  {generatedStoryText}
                </div>
                
                <div className="story-actions" style={{
                  marginTop: '25px',
                  display: 'flex',
                  justifyContent: 'center',
                  gap: '15px'
                }}>
                  <button
                    onClick={handleDownloadStory}
                    className="btn-download"
                    style={{
                      padding: '10px 20px',
                      backgroundColor: '#4CAF50',
                      color: 'white',
                      border: 'none',
                      borderRadius: '6px',
                      cursor: 'pointer',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '8px',
                      fontSize: '1rem'
                    }}
                  >
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                      <path d="M12 4V16M12 16L7 11M12 16L17 11M6 20H18" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                    </svg>
                    Download Story
                  </button>
                  
                  <button
                    onClick={handleRandomStory}
                    disabled={isLoading}
                    className="btn-another"
                    style={{
                      padding: '10px 20px',
                      backgroundColor: '#007bff',
                      color: 'white',
                      border: 'none',
                      borderRadius: '6px',
                      cursor: 'pointer',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '8px',
                      fontSize: '1rem'
                    }}
                  >
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                      <path d="M4 4v7h7M20 20v-7h-7M20 4l-7 7M4 20l7-7" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                    </svg>
                    Generate Another
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
  );
};

export default RandomStory;

