import axios from 'axios';


const API_URL = 'http://localhost:5000';

// Configure axios defaults
axios.defaults.headers.common['Access-Control-Allow-Origin'] = '*';
axios.defaults.headers.common['Content-Type'] = 'application/json';

const PAGE_SIZE = 12; // Number of videos to load per page (3 columns x 4 rows)

export const searchVideos = async (query, offset = 0, limit = PAGE_SIZE) => {
  try {
    const response = await axios.post(`${API_URL}/search`, {
      query,
      offset,
      limit
    });
    
    return {
      results: response.data.results || [],
      hasMore: response.data.has_more || false,
      total: response.data.total || 0
    };
  } catch (error) {
    console.error('Error searching videos:', error);
    throw error;
  }
};

export const getInitialVideos = async (offset = 0, limit = PAGE_SIZE) => {
  try {
    const response = await axios.get(`${API_URL}/initial-videos`, {
      params: {
        offset,
        limit
      }
    });
    
    return {
      videos: response.data.videos || [],
      hasMore: response.data.has_more || false,
      total: response.data.total || 0
    };
  } catch (error) {
    console.error('Error fetching initial videos:', error);
    throw error;
  }
};