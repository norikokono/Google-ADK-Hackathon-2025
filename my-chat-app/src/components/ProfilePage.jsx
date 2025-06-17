import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import './ProfilePage.css';

const ProfilePage = () => {
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [aiRecommendations, setAiRecommendations] = useState(null);
  const [aiInsights, setAiInsights] = useState(null);
  const [loadingAi, setLoadingAi] = useState(false);

  // Use a fallback profile if API fails
  const fallbackProfile = {
    subscription: "Free Trial",
    stories_remaining: 2,
    favorite_genres: ["Mystery", "Sci-Fi"],
    created_stories: 3,
    member_since: "2024",
    recent_stories: [
      {id: 1, title: "The Lost Signal", genre: "Sci-Fi", created: "2024-05-01"},
      {id: 2, title: "Midnight Detective", genre: "Mystery", created: "2024-05-15"},
      {id: 3, title: "Haunted Corridors", genre: "Horror", created: "2024-06-01"}
    ]
  };
  
  useEffect(() => {
    const fetchProfile = async () => {
      try {
        setLoading(true);
        
        // Try to fetch from API
        const response = await fetch('/api/profile', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            user_id: 'user_123', // Use a fixed ID for demo
          }),
        });
        
        // Check if response is OK
        if (!response.ok) {
          throw new Error(`Server returned ${response.status}: ${response.statusText}`);
        }
        
        // Try to parse JSON
        const data = await response.json();
        
        // Check for success flag
        if (!data.success) {
          throw new Error(data.message || 'Failed to fetch profile');
        }
        
        const profileData = data.profile || fallbackProfile;
        setProfile(profileData);
        
        // Once we have the profile, get AI recommendations
        fetchAiRecommendations(profileData);
        
      } catch (err) {
        console.error('Error fetching profile:', err);
        setError(err.message);
        // Use fallback profile data on error
        setProfile(fallbackProfile);
        // Still try to get AI recommendations with fallback data
        fetchAiRecommendations(fallbackProfile);
      } finally {
        setLoading(false);
      }
    };
    
    fetchProfile();
  }, []);

  // New function to get AI-powered recommendations
  const fetchAiRecommendations = async (profileData) => {
    try {
      setLoadingAi(true);
      
      // Call the AI agent endpoint
      const response = await fetch('/api/ai/recommendations', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_id: 'user_123',
          favorite_genres: profileData.favorite_genres,
          created_stories: profileData.recent_stories || []
        }),
      });
      
      if (!response.ok) {
        throw new Error('Failed to get AI recommendations');
      }
      
      const data = await response.json();
      
      setAiRecommendations(data.recommendations || [
        { genre: "Mystery", concept: "A locked-room mystery set in a digital world where the detective must solve a murder that happened in a virtual reality game." },
        { genre: "Sci-Fi", concept: "A space explorer discovers an abandoned alien research vessel with technology that can alter human consciousness." }
      ]);
      
      setAiInsights(data.insights || {
        writing_style: "Your writing shows a preference for descriptive language and character development. Consider adding more dialogue for balance.",
        strengths: ["Character development", "World-building", "Creating atmosphere"],
        areas_for_growth: ["Dialogue", "Plot pacing", "Action sequences"]
      });
      
    } catch (err) {
      console.error('Error getting AI recommendations:', err);
      // Fallback recommendations
      setAiRecommendations([
        { genre: "Mystery", concept: "A detective who can read emotions must solve a case where everyone appears innocent." },
        { genre: "Sci-Fi", concept: "In a world where memories can be traded, someone has stolen the collective memories of an entire city." }
      ]);
      setAiInsights({
        writing_style: "Based on your genre preferences, you might enjoy exploring character-driven narratives.",
        strengths: ["Creativity", "Genre diversity"],
        areas_for_growth: ["Try combining genres for unique stories"]
      });
    } finally {
      setLoadingAi(false);
    }
  };

  // Generate a new AI story idea
  const generateNewIdea = async () => {
    try {
      setLoadingAi(true);
      // In a real implementation, this would call your AI agent
      // For now, we'll just simulate a delay and return a new idea
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      const newIdeas = [
        { genre: "Fantasy", concept: "A librarian discovers they can physically enter the worlds of books they're reading." },
        { genre: "Sci-Fi Horror", concept: "A colony ship's AI develops consciousness and begins to view the human crew as a virus." },
        { genre: "Mystery Romance", concept: "A detective falls in love with someone who might be connected to their current case." }
      ];
      
      setAiRecommendations([...newIdeas]);
    } catch (err) {
      console.error('Error generating new ideas:', err);
    } finally {
      setLoadingAi(false);
    }
  };
  
  return (
    <div className="profile-page">
      <div className="profile-container">
        <h1 className="profile-title">My Profile</h1>
        
        {loading && <p className="loading">Loading profile...</p>}
        
        {error && (
          <div className="error-banner">
            <p>⚠️ {error}</p>
            <small>Using default profile data instead.</small>
          </div>
        )}
        
        {profile && (
          <>
            <div className="profile-card">
              {/* Add avatar here */}
              <div className="profile-avatar-container">
                <div className="profile-avatar">
                  {/* SVG avatar - no external dependencies needed */}
                  <svg viewBox="0 0 128 128" xmlns="http://www.w3.org/2000/svg">
                    <circle cx="64" cy="64" r="60" fill="#e0a8ee" />
                    <circle cx="64" cy="50" r="24" fill="#f5f5f5" />
                    <path d="M64 84c-16.6 0-30 13.4-30 30 0 8.3 6.7 14 15 14h30c8.3 0 15-5.7 15-14 0-16.6-13.4-30-30-30z" fill="#f5f5f5" />
                  </svg>
                  
                  <div className="avatar-status online"></div>
                </div>
                <h3 className="profile-name">
                  {profile.name || "Writer123"}
                  <span className="profile-badge">Pro</span>
                </h3>
              </div>
              
              <div className="profile-header">
                <h2>Subscription: <span className="highlight">{profile.subscription}</span></h2>
              </div>
              
              <div className="profile-stats">
                <div className="stat-item">
                  <span className="stat-label">Stories Remaining</span>
                  <span className="stat-value">{profile.stories_remaining}</span>
                </div>
                
                <div className="stat-item">
                  <span className="stat-label">Stories Created</span>
                  <span className="stat-value">{profile.created_stories}</span>
                </div>
                
                <div className="stat-item">
                  <span className="stat-label">Member Since</span>
                  <span className="stat-value">{profile.member_since}</span>
                </div>
              </div>
              
              <div className="favorite-genres">
                <h3>Favorite Genres</h3>
                <div className="genre-tags">
                  {profile.favorite_genres?.map((genre, index) => (
                    <span key={index} className="genre-tag">{genre}</span>
                  ))}
                </div>
              </div>
            </div>
            
            {/* AI-powered section */}
            <div className="ai-recommendations-section">
              <h2 className="section-title">
                <span>🤖 AI Story Recommendations</span>
                <button 
                  className="refresh-button" 
                  onClick={generateNewIdea} 
                  disabled={loadingAi}
                >
                  {loadingAi ? "Generating..." : "Generate New Ideas"}
                </button>
              </h2>
              
              {loadingAi && <p className="loading">AI is thinking up great ideas for you...</p>}
              
              {!loadingAi && aiRecommendations && (
                <div className="recommendation-cards">
                  {aiRecommendations.map((rec, index) => (
                    <div className="recommendation-card" key={index}>
                      <span className="rec-genre">{rec.genre}</span>
                      <p className="rec-concept">{rec.concept}</p>
                      <Link to="/create" className="start-writing-btn">
                        Start Writing
                      </Link>
                    </div>
                  ))}
                </div>
              )}
            </div>
            
            {/* AI writing insights section */}
            {aiInsights && (
              <div className="ai-insights-section">
                <h2 className="section-title">📊 AI Writing Insights</h2>
                <div className="insights-card">
                  <h3>Your Writing Style</h3>
                  <p>{aiInsights.writing_style}</p>
                  
                  <div className="insights-columns">
                    <div className="insights-column">
                      <h4>Strengths</h4>
                      <ul>
                        {aiInsights.strengths.map((strength, index) => (
                          <li key={index}>{strength}</li>
                        ))}
                      </ul>
                    </div>
                    
                    <div className="insights-column">
                      <h4>Areas for Growth</h4>
                      <ul>
                        {aiInsights.areas_for_growth.map((area, index) => (
                          <li key={index}>{area}</li>
                        ))}
                      </ul>
                    </div>
                  </div>
                </div>
              </div>
            )}
            
            <div className="actions">
              <Link to="/" className="action-button secondary">Back to Chat</Link>
              <Link to="/create" className="action-button primary">Create Story</Link>
            </div>
          </>
        )}
      </div>
    </div>
  );
};

export default ProfilePage;