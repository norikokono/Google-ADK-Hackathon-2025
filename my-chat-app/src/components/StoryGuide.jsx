import React, { useState } from 'react';
import './StoryGuide.css';

const StoryGuide = () => {
  const [generatedStory, setGeneratedStory] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const categories = {
    genres: [
      { name: 'mystery', description: 'Detective stories and puzzles' },
      { name: 'scifi', description: 'Future and technology' },
      { name: 'fantasy', description: 'Magic and wonder' },
      { name: 'romance', description: 'Love and relationships' },
      { name: 'adventure', description: 'Action and excitement' },
      { name: 'horror', description: 'Suspense and fear' },
      { name: 'comedy', description: 'Humor and fun' },
      { name: 'thriller', description: 'Intense suspense and plot twists' },
      { name: 'historical', description: 'Past events and periods' },
      { name: 'western', description: 'Frontier and cowboys' },
      { name: 'cyberpunk', description: 'Dystopian tech future' }
    ],
    moods: [
      { name: 'mysterious', description: 'Intriguing and suspenseful' },
      { name: 'whimsical', description: 'Light and playful' },
      { name: 'dark', description: 'Serious and moody' },
      { name: 'romantic', description: 'Warm and emotional' },
      { name: 'epic', description: 'Grand and inspiring' },
      { name: 'funny', description: 'Humorous and amusing' },
      { name: 'melancholic', description: 'Sad and thoughtful' },
      { name: 'suspenseful', description: 'Tense and exciting' },
      { name: 'nostalgic', description: 'Longing for the past' },
      { name: 'dreamy', description: 'Visionary and ethereal' },
      { name: 'tense', description: 'Stressful and strained' },
      { name: 'peaceful', description: 'Calm and tranquil' },
      { name: 'chaotic', description: 'Disordered and turbulent' }
    ],
    lengths: [
      { name: 'micro', description: '~100 words (2-3 min read)' },
      { name: 'short', description: '~500 words (5-7 min read)' },
      { name: 'medium', description: '~1000 words (10-12 min read)' },
      { name: 'long', description: '~2000 words (15-20 min read)' }
    ]
  };

  // Helper function that generates a story based on the selected genre, mood, and length.
  const generateStoryText = (genre, mood, length) => {
    const genreIntros = {
      mystery: "In the fog-shrouded streets",
      scifi: "Among the gleaming spires of a distant colony",
      fantasy: "In a realm where magic flows like water",
      romance: "Under the soft glow of twilight",
      adventure: "Beyond the boundaries of the known world",
      horror: "As darkness crept through abandoned halls",
      comedy: "In what could only be described as cosmic irony",
      thriller: "Through the twisting corridors of intrigue",
      historical: "In an age when legends were born",
      western: "Across the untamed frontier",
      cyberpunk: "Beneath the neon-drenched megalopolis"
    };

    const moodDescriptions = {
      mysterious: "where secrets whisper from shadows",
      whimsical: "where reality dances with imagination",
      dark: "where light fears to linger",
      romantic: "where hearts speak louder than words",
      epic: "where destiny calls the brave",
      funny: "where absurdity reigns supreme",
      melancholic: "where memories paint the present",
      suspenseful: "where every moment hangs by a thread",
      nostalgic: "where time flows like honey",
      dreamy: "where reality blurs at the edges",
      tense: "where danger lurks at every turn",
      peaceful: "where tranquility wraps all in its embrace",
      chaotic: "where order dissolves into mayhem"
    };

    const intro = `${genreIntros[genre.name] || "In a world"} ${moodDescriptions[mood.name] || "of endless possibility"}`;
    
    // Consider mood when generating length-specific content
    const moodLengthContent = {
      mysterious: {
        micro: "a single clue changes everything",
        short: "secrets begin to unravel",
        medium: "layers of mystery peel away",
        long: "an intricate web of deception unfolds"
      },
      tense: {
        micro: "time runs dangerously short",
        short: "pressure builds steadily",
        medium: "stakes escalate dramatically",
        long: "tension mounts to breaking point"
      },
      peaceful: {
        micro: "finding perfect serenity",
        short: "peace blossoms naturally",
        medium: "tranquility deepens gradually",
        long: "harmony spreads like gentle waves"
      }
    };

    const moodContent = moodLengthContent[mood.name]?.[length.name] || "";
    
    switch (length.name.toLowerCase()) {
      case 'micro':
        return `${intro}, where ${moodContent || "our tale unfolds in a fleeting moment of crystallized possibility"}.`;
      case 'short':
        return `${intro}, where ${moodContent || "we discover a story that weaves through the fabric of imagination"}.`;
      case 'medium':
        return `${intro}, where ${moodContent || "we embark on a journey that will reshape the landscape of possibility"}.`;
      case 'long':
        return `${intro}, where ${moodContent || "we begin an epic voyage through realms of wonder and revelation"}.`;
      default:
        return "Invalid length selected.";
    }
  };

  // Get complementary moods for a genre
  const getComplementaryMoods = (genre) => {
    const complementaryMoods = {
      mystery: ['mysterious', 'suspenseful', 'tense', 'dark'],
      scifi: ['epic', 'mysterious', 'dark', 'peaceful'],
      fantasy: ['whimsical', 'epic', 'dreamy', 'mysterious'],
      romance: ['romantic', 'nostalgic', 'peaceful', 'dreamy'],
      adventure: ['epic', 'suspenseful', 'chaotic', 'whimsical'],
      horror: ['dark', 'tense', 'suspenseful', 'mysterious'],
      comedy: ['funny', 'whimsical', 'chaotic', 'peaceful'],
      thriller: ['suspenseful', 'tense', 'dark', 'mysterious'],
      historical: ['nostalgic', 'epic', 'melancholic', 'romantic'],
      western: ['nostalgic', 'tense', 'peaceful', 'suspenseful'],
      cyberpunk: ['dark', 'chaotic', 'tense', 'melancholic']
    };
    return complementaryMoods[genre] || ['mysterious', 'epic', 'peaceful'];
  };

  // When clicked, randomly choose a genre, mood, and length; then generate the story.
  const handleGenerateStory = async () => {
    const randomGenre = 
      categories.genres[Math.floor(Math.random() * categories.genres.length)];
    const randomMood =
      categories.moods[Math.floor(Math.random() * categories.moods.length)];
    const randomLength =
      categories.lengths[Math.floor(Math.random() * categories.lengths.length)];
    
    setIsLoading(true);
    
    try {
      // Call your API to generate the actual story
      const response = await fetch('/api/generate-story', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          genre: randomGenre.name,
          mood: randomMood.name,
          length: randomLength.name
        })
      });
      
      const data = await response.json();
      setGeneratedStory(data.story);
    } catch (error) {
      console.error('Error generating story:', error);
      setGeneratedStory('Failed to generate story. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="story-guide">
      <header className="guide-header">
        <h1>📝 Story Creation Guide</h1>
        <p className="format-hint">Format: genre | mood | length</p>
      </header>

      <section className="examples" style={{ 
        margin: '0 0 15px 0',  // Reduced bottom margin
        padding: '0'           // Removed padding
      }}>
        <h2 style={{ 
          marginBottom: '6px',  // Reduced space after heading
          fontSize: '1.2em'     // Slightly smaller heading
        }}>✨ Quick Examples</h2>
        <ul style={{ 
          margin: '0', 
          padding: '0 0 0 5px',  // Only keep minimal left padding
          listStylePosition: 'inside' 
        }}>
          <li style={{ margin: '1px 0', fontSize: '0.95em' }}>mystery | mysterious | short - Perfect for beginners</li>
          <li style={{ margin: '1px 0', fontSize: '0.95em' }}>fantasy | whimsical | micro - Quick magical tales</li>
          <li style={{ margin: '1px 0', fontSize: '0.95em' }}>scifi | dark | medium - Deep space adventures</li>
          <li style={{ margin: '1px 0', fontSize: '0.95em' }}>cyberpunk | tense | short - Neon-lit thrillers</li>
          <li style={{ margin: '1px 0', fontSize: '0.95em' }}>western | nostalgic | medium - Frontier tales</li>
        </ul>
      </section>

      <div className="categories-grid" style={{ 
        display: 'grid', 
        gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', 
        gap: '15px',  // Reduced gap between grid items
        marginBottom: '20px'
      }}>
        <section className="category" style={{ margin: 0 }}>  {/* Removed margin */}
          <h2 style={{ marginBottom: '8px' }}>🎭 Genres</h2>  {/* Reduced bottom margin */}
          <ul style={{ 
            margin: 0, 
            padding: 0, 
            listStylePosition: 'inside' 
          }}>
            {categories.genres.map(genre => (
              <li key={genre.name} style={{ 
                margin: '2px 0',  // Minimal vertical spacing
                paddingLeft: '5px',
                fontSize: '0.95em'  // Slightly smaller font
              }}>
                <strong>{genre.name}</strong> - {genre.description}
              </li>
            ))}
          </ul>
        </section>

        <section className="category" style={{ margin: 0 }}>  {/* Removed margin */}
          <h2 style={{ marginBottom: '8px' }}>🌟 Moods</h2>  {/* Reduced bottom margin */}
          <ul style={{ 
            margin: 0, 
            padding: 0, 
            listStylePosition: 'inside' 
          }}>
            {categories.moods.map(mood => (
              <li key={mood.name} style={{ 
                margin: '2px 0',  // Minimal vertical spacing
                paddingLeft: '5px',
                fontSize: '0.95em'  // Slightly smaller font
              }}>
                <strong>{mood.name}</strong> - {mood.description}
              </li>
            ))}
          </ul>
        </section>

        <section className="category" style={{ margin: 0 }}>  {/* Removed margin */}
          <h2 style={{ marginBottom: '8px' }}>📏 Lengths</h2>  {/* Reduced bottom margin */}
          <ul style={{ 
            margin: 0, 
            padding: 0, 
            listStylePosition: 'inside' 
          }}>
            {categories.lengths.map(length => (
              <li key={length.name} style={{ 
                margin: '2px 0',  // Minimal vertical spacing
                paddingLeft: '5px',
                fontSize: '0.95em'  // Slightly smaller font
              }}>
                <strong>{length.name}</strong> - {length.description}
              </li>
            ))}
          </ul>
        </section>
      </div>

      <section className="pro-tips">
        <h2>💡 Pro Tips</h2>
        <ul>
          <li>Pair classic combinations: mystery + suspenseful, romance + dreamy</li>
          <li>Try contrasts: cyberpunk + nostalgic, historical + whimsical</li>
          <li>Start with micro stories (100 words) to experiment with styles</li>
          <li>Match intensity: thriller + tense, fantasy + epic</li>
          <li>Create atmosphere: horror + dark, western + peaceful</li>
          <li>Mix timeframes: historical + chaotic, scifi + melancholic</li>
        </ul>
      </section>
      
      {generatedStory && (
        <section className="generated-story">
          <h2>Generated Story</h2>
          <p style={{ whiteSpace: 'pre-wrap' }}>{generatedStory}</p>
        </section>
      )}
    </div>
  );
};

export default StoryGuide;
