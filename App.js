import React, { useState } from "react";
import "./App.css";

function App() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);

  const handleSearch = async () => {
    if (!query.trim()) return;
    setLoading(true);

    try {
      const response = await fetch("http://127.0.0.1:8000/search", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query }),
      });

      const data = await response.json();
      setResults(data.results || []);
    } catch (error) {
      console.error("Error fetching results:", error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="App">
      {/* Background video */}
      <video autoPlay loop muted playsInline className="background-video">
        <source
          src="https://videos.pexels.com/video-files/855869/855869-sd_640_360_25fps.mp4"
          type="video/mp4"
        />
      </video>

      {/* Overlay content */}
      <div className="overlay">
        <header className="header">
          <h1 className="glow-text">
            Query<span className="tube">Tube</span>
          </h1>
          <p className="tagline">Search smarter. Discover faster. 🔍</p>
        </header>

        {/* Search bar */}
        <div className="search-bar">
          <input
            type="text"
            value={query}
            placeholder="Type your question about AI, tech, or anything..."
            onChange={(e) => setQuery(e.target.value)}
          />
          <button onClick={handleSearch} disabled={loading}>
            {loading ? "Searching..." : "Search"}
          </button>
        </div>

        {/* Results */}
        <div className="results-container">
          {results.length > 0 && (
            <div className="results-grid">
              {results.map((item, i) => (
                <div key={item.video_id} className="result-card">
                  <div className="card-glow" />

                  {/* Thumbnail */}
                  <div className="thumbnail-container">
                    <img
                      src={`https://img.youtube.com/vi/${item.video_id}/hqdefault.jpg`}
                      alt={item.title}
                      className="thumbnail"
                      loading="lazy"
                    />
                  </div>

                  <h3 className="video-title">
                    {i + 1}. {item.title}
                  </h3>
                  <p><strong> Video ID:</strong> {item.video_id}</p>
                  <p><strong> Similarity:</strong> {item.similarity_score.toFixed(4)}</p>
                  <p className="transcript">{item.transcript}</p>

                  <a
                    href={`https://www.youtube.com/watch?v=${item.video_id}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="watch-button"
                  >
                    ▶ Watch on YouTube
                  </a>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default App;
