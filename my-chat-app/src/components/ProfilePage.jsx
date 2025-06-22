import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import './ProfilePage.css';
import { fetchAPI } from '../utils/api';

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

const fallbackRecommendations = [
  { genre: "Mystery", concept: "A detective who can read emotions must solve a case where everyone appears innocent." },
  { genre: "Sci-Fi", concept: "In a world where memories can be traded, someone has stolen the collective memories of an entire city." }
];

const fallbackInsights = {
  writing_style: "Based on your genre preferences, you might enjoy exploring character-driven narratives.",
  strengths: ["Creativity", "Genre diversity"],
  areas_for_growth: ["Try combining genres for unique stories"]
};

const ProfilePage = () => {
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [aiRecommendations, setAiRecommendations] = useState(null);
  const [aiInsights, setAiInsights] = useState(null);
  const [loadingAi, setLoadingAi] = useState(false);

  useEffect(() => {
    const fetchProfile = async () => {
      try {
        setLoading(true);
        const data = await fetchAPI('/api/profile', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            user_id: 'user_123',
          }),
        });

        // If the backend returns a profile object, use it; otherwise fallback
        const profileData = data && typeof data === 'object' && !Array.isArray(data)
          ? data
          : fallbackProfile;
        setProfile(profileData);

        fetchAiRecommendations(profileData);
      } catch (err) {
        setError('Failed to fetch profile. Using default profile.');
        setProfile(fallbackProfile);
        fetchAiRecommendations(fallbackProfile);
      } finally {
        setLoading(false);
      }
    };

    fetchProfile();
    // eslint-disable-next-line
  }, []);

  const fetchAiRecommendations = async (profileData) => {
    try {
      setLoadingAi(true);
      const data = await fetchAPI('/api/ai/recommendations', {
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

      setAiRecommendations(data.recommendations || fallbackRecommendations);
      setAiInsights(data.insights || fallbackInsights);
    } catch (err) {
      setAiRecommendations(fallbackRecommendations);
      setAiInsights(fallbackInsights);
    } finally {
      setLoadingAi(false);
    }
  };

  const generateNewIdea = async () => {
    try {
      setLoadingAi(true);
      // Simulate a delay for demo
      await new Promise(resolve => setTimeout(resolve, 1000));
      const newIdeas = [
        { genre: "Fantasy", concept: "A librarian discovers they can physically enter the worlds of books they're reading." },
        { genre: "Sci-Fi Horror", concept: "A colony ship's AI develops consciousness and begins to view the human crew as a virus." },
        { genre: "Mystery Romance", concept: "A detective falls in love with someone who might be connected to their current case." }
      ];
      setAiRecommendations([...newIdeas]);
    } catch (err) {
      // fallback already handled
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
              <div className="profile-avatar-container">
                <div className="profile-avatar">
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