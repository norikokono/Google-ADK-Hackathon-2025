const API_URL = 'https://plotbuddy-api-63800697128.us-central1.run.app'; // Paste your Cloud Run URL here

export const fetchAPI = async (endpoint, options = {}) => {
  const url = `${API_URL}${endpoint}`;
  const response = await fetch(url, options);
  if (!response.ok) throw new Error(`Server returned ${response.status}`);
  return response.json(); // <--- THIS IS CORRECT
};