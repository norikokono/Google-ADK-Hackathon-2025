// If you haven't created this file yet:

// For local development (temporary)
const API_URL = 'http://localhost:8000';

// Once your Cloud Run deployment is ready, change to:
// const API_URL = 'https://plotbuddy-api-xxxx-xx.a.run.app'; // Your Cloud Run URL

export const fetchAPI = async (endpoint, options = {}) => {
  const url = `${API_URL}${endpoint}`;
  console.log(`Fetching from: ${url}`);
  
  try {
    const response = await fetch(url, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...(options.headers || {})
      }
    });
    
    if (!response.ok) {
      throw new Error(`Server returned ${response.status}`);
    }
    
    return response.json();
  } catch (error) {
    console.error(`API error for ${endpoint}:`, error);
    throw error;
  }
};