const BACKEND_URL = "http://127.0.0.1:8000";
// 🔧 Helper function to fix thumbnail URLs using the YouTube video ID
function fixThumbnailURLs(videos) {
  return videos.map(video => {
    let thumb = video.thumbnail || "";
    let videoId = null;

    // Extract video ID from the YouTube URL
    if (video.url && video.url.includes("v=")) {
      videoId = video.url.split("v=")[1];
      // Remove any extra parameters (like &t=)
      if (videoId.includes("&")) {
        videoId = videoId.split("&")[0];
      }
    }

    // If we found a valid ID, use it to construct the correct thumbnail URL
    if (videoId) {
      thumb = `https://i.ytimg.com/vi/${videoId}/hqdefault.jpg`;
    } else {
      // Fallback: official YouTube logo
      thumb = "https://upload.wikimedia.org/wikipedia/commons/b/b8/YouTube_Logo_2017.svg";
    }

    return { ...video, thumbnail: thumb };
  });
}

async function searchVideos() {
  const query = document.getElementById("query").value.trim();
  const resultsContainer = document.getElementById("results-container");
  const loadingText = document.getElementById("loading");

  resultsContainer.innerHTML = "";
  if (!query) {
    alert("Please enter a search term");
    return;
  }

  loadingText.style.display = "block";

  try {
    const response = await fetch(`${BACKEND_URL}/query?query=${encodeURIComponent(query)}&top_k=5`);
    if (!response.ok) throw new Error("Backend not reachable");

    const data = await response.json();
    loadingText.style.display = "none";

    if (!data.results || data.results.length === 0) {
      resultsContainer.innerHTML = "<p>No results found.</p>";
      return;
    }
    
     data.results = fixThumbnailURLs(data.results);
    
    resultsContainer.innerHTML = data.results
      .map(
        (video) => `
        <div class="result-card">
          <img src="${video.thumbnail}" alt="${video.title}" />
          <a href="${video.url}" target="_blank" class="result-title">${video.title}</a>
          <div class="result-channel">${video.channel_title}</div>
          <div class="result-description">${video.description}</div>
          <div class="score">Similarity: ${video.similarity_score}</div>
        </div>`
      )
      .join("");
  } catch (error) {
    console.error(error);
    loadingText.style.display = "none";
    resultsContainer.innerHTML = `<p style="color:red;">Backend not reachable. Make sure FastAPI is running.</p>`;
  }
}
