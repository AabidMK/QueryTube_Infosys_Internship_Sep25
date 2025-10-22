import axios from "axios";

// Configuration
const API_BASE_URL = "http://127.0.0.1:8000"; // Your actual API endpoint
const API_TIMEOUT = 30000;

// Create axios instance
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
    "Accept": "application/json",
  },
  timeout: API_TIMEOUT,
});

/**
 * Searches videos based on a semantic query and pagination.
 * @param {string} query The natural language search query.
 * @param {number} page Page number for pagination.
 * @param {number} page_size Number of results per page.
 * @returns {Promise<{results: Object[], meta: Object}>} Search results and metadata.
 */
export const searchVideos = async ({ query, page, page_size }) => {
  if (!query) {
    return { results: [], meta: { page: 1, page_size: page_size || 20, total_results: 0 } };
  }

  try {
    // Make actual API call to your backend
    const response = await apiClient.post("/search", {
      query: query,
      top_k: page_size || 20,
      // removed category filtering (categories removed)
    });

    // Handle the response format from your API
    if (response.data.status === "success") {
      const results = response.data.results || [];
      const total = response.data.total_results || results.length;
      
      console.log('API Response:', response.data);
      console.log('First result thumbnail in backend:', results[0]?.thumbnail_high);
      
      // Map the API response to match frontend expectations
      const mappedResults = results.map((item, index) => ({
        rank: item.rank || index + 1,
        title: item.title || "Untitled Video",
        video_id: item.video_id,
        channel_title: item.channel || "Unknown Channel",
        view_count: item.view_count || 0,
        like_count: item.like_count || 0,
        duration: item.duration || "0",
        published_at: item.published_at || null,
        similarity_score: item.similarity_score || 0,
        transcript_preview: item.transcript ? item.transcript.substring(0, 200) + "..." : "",
        thumbnail_url: item.thumbnail_high || null
      }));
      
      console.log('Mapped results:', mappedResults);

      return {
        results: mappedResults,
        meta: {
          page: page || 1,
          page_size: page_size || 20,
          total_results: total
        }
      };
    } else {
      throw new Error("API returned unsuccessful status");
    }

  } catch (error) {
    console.error("Search failed:", error);
    
    // Check if it's a network error
    if (error.code === 'ERR_NETWORK' || (error.message && error.message.includes('Network Error'))) {
      throw new Error(`Cannot connect to API at ${API_BASE_URL}. Please ensure the backend is running.`);
    }
    
    throw new Error(`Failed to fetch results: ${error.message || error}`);
  }
};

