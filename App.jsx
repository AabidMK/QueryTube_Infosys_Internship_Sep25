import React, { useState } from "react";

function App() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [searched, setSearched] = useState(false);

  const handleSearch = async () => {
    if (!query.trim()) {
      setError("Please enter a search query");
      return;
    }
    
    setLoading(true);
    setError("");
    setSearched(true);

    try {
      const response = await fetch("http://127.0.0.1:8000/search", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: query.trim(), top_k: 5, min_similarity: 0.1 }),
      });

      if (!response.ok) throw new Error("Search failed. Please try again.");
      const data = await response.json();
      setResults(data.results || []);
    } catch (err) {
      setError(err.message);
      setResults([]);
    } finally {
      setLoading(false);
    }
  };

  const getSimilarityColor = (similarity) => {
    if (similarity >= 0.8) return "#10b981";
    if (similarity >= 0.6) return "#3b82f6";
    return "#f59e0b";
  };

  const getSimilarityBgColor = (similarity) => {
    if (similarity >= 0.8) return "#d1fae5";
    if (similarity >= 0.6) return "#dbeafe";
    return "#fef3c7";
  };

  return (
    <div style={{
      minHeight: "100vh",
      background: "linear-gradient(135deg, #f8fafc 0%, #e0f2fe 50%, #ddd6fe 100%)",
      fontFamily: "'Inter', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif"
    }}>
      {/* Header */}
      <header style={{
        backgroundColor: "#ffffff",
        borderBottom: "1px solid #e2e8f0",
        boxShadow: "0 1px 3px rgba(0,0,0,0.05)"
      }}>
        <div style={{
          maxWidth: "1280px",
          margin: "0 auto",
          padding: "24px 20px",
          display: "flex",
          alignItems: "center",
          gap: "12px"
        }}>
          <svg style={{ width: "32px", height: "32px" }} fill="#dc2626" viewBox="0 0 24 24">
            <path d="M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z"/>
          </svg>
          <div>
            <h1 style={{ fontSize: "28px", fontWeight: "700", color: "#0f172a", margin: 0 }}>
             AI QueryTube 
            </h1>
            <p style={{ fontSize: "13px", color: "#64748b", margin: "4px 0 0 0" }}>
              Semantic Search for YouTube Videos
            </p>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main style={{ maxWidth: "1280px", margin: "0 auto", padding: "32px 20px" }}>
        {/* Search Section */}
        <div style={{
          backgroundColor: "#ffffff",
          borderRadius: "16px",
          boxShadow: "0 10px 25px rgba(0,0,0,0.08)",
          padding: "32px",
          marginBottom: "32px"
        }}>
          <div style={{ position: "relative", marginBottom: "16px" }}>
            <svg style={{
              position: "absolute",
              left: "16px",
              top: "50%",
              transform: "translateY(-50%)",
              width: "20px",
              height: "20px",
              color: "#94a3b8"
            }} fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
              placeholder="Search for videos using natural language..."
              style={{
                width: "100%",
                paddingLeft: "48px",
                paddingRight: "16px",
                paddingTop: "16px",
                paddingBottom: "16px",
                fontSize: "16px",
                border: "2px solid #e2e8f0",
                borderRadius: "12px",
                outline: "none",
                transition: "all 0.3s",
                boxSizing: "border-box"
              }}
              onFocus={(e) => {
                e.target.style.borderColor = "#3b82f6";
                e.target.style.boxShadow = "0 0 0 4px rgba(59, 130, 246, 0.1)";
              }}
              onBlur={(e) => {
                e.target.style.borderColor = "#e2e8f0";
                e.target.style.boxShadow = "none";
              }}
            />
          </div>

          <button
            onClick={handleSearch}
            disabled={loading}
            style={{
              width: "100%",
              background: loading ? "#94a3b8" : "linear-gradient(135deg, #2563eb 0%, #4f46e5 100%)",
              color: "#ffffff",
              fontWeight: "600",
              fontSize: "16px",
              padding: "16px 24px",
              borderRadius: "12px",
              border: "none",
              cursor: loading ? "not-allowed" : "pointer",
              boxShadow: loading ? "none" : "0 4px 14px rgba(37, 99, 235, 0.3)",
              transition: "all 0.3s",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              gap: "8px"
            }}
            onMouseEnter={(e) => {
              if (!loading) {
                e.target.style.background = "linear-gradient(135deg, #1d4ed8 0%, #4338ca 100%)";
                e.target.style.transform = "translateY(-2px)";
                e.target.style.boxShadow = "0 6px 20px rgba(37, 99, 235, 0.4)";
              }
            }}
            onMouseLeave={(e) => {
              if (!loading) {
                e.target.style.background = "linear-gradient(135deg, #2563eb 0%, #4f46e5 100%)";
                e.target.style.transform = "translateY(0)";
                e.target.style.boxShadow = "0 4px 14px rgba(37, 99, 235, 0.3)";
              }
            }}
          >
            {loading ? (
              <>
                <div style={{
                  width: "20px",
                  height: "20px",
                  border: "2px solid #ffffff",
                  borderTopColor: "transparent",
                  borderRadius: "50%",
                  animation: "spin 1s linear infinite"
                }} />
                Searching...
              </>
            ) : (
              <>
                <svg style={{ width: "20px", height: "20px" }} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
                Search Videos
              </>
            )}
          </button>

          {error && (
            <div style={{
              marginTop: "16px",
              padding: "16px",
              backgroundColor: "#fef2f2",
              border: "1px solid #fecaca",
              borderRadius: "8px",
              color: "#b91c1c"
            }}>
              {error}
            </div>
          )}
        </div>

        {/* Results Section */}
        {searched && !loading && (
          <div>
            {results.length > 0 ? (
              <>
                <div style={{
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "space-between",
                  marginBottom: "24px"
                }}>
                  <h2 style={{ fontSize: "24px", fontWeight: "700", color: "#0f172a", margin: 0 }}>
                    Top {results.length} Results
                  </h2>
                  <div style={{
                    display: "flex",
                    alignItems: "center",
                    gap: "8px",
                    fontSize: "14px",
                    color: "#64748b"
                  }}>
                    <svg style={{ width: "16px", height: "16px" }} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
                    </svg>
                    Ranked by semantic similarity
                  </div>
                </div>

                <div style={{ display: "flex", flexDirection: "column", gap: "24px" }}>
                  {results.map((result, index) => (
                    <div
                      key={index}
                      style={{
                        backgroundColor: "#ffffff",
                        borderRadius: "12px",
                        boxShadow: "0 4px 12px rgba(0,0,0,0.08)",
                        overflow: "hidden",
                        border: "1px solid #e2e8f0",
                        transition: "all 0.3s"
                      }}
                      onMouseEnter={(e) => {
                        e.currentTarget.style.boxShadow = "0 8px 24px rgba(0,0,0,0.12)";
                        e.currentTarget.style.transform = "translateY(-2px)";
                      }}
                      onMouseLeave={(e) => {
                        e.currentTarget.style.boxShadow = "0 4px 12px rgba(0,0,0,0.08)";
                        e.currentTarget.style.transform = "translateY(0)";
                      }}
                    >
                      <div style={{
                        display: "flex",
                        flexDirection: window.innerWidth < 768 ? "column" : "row"
                      }}>
                        {/* Thumbnail */}
                        <div style={{ flexShrink: 0, width: window.innerWidth < 768 ? "100%" : "320px" }}>
                          <a
                            href={result.video_url}
                            target="_blank"
                            rel="noopener noreferrer"
                            style={{ display: "block", position: "relative" }}
                          >
                            <img
                              src={result.thumbnail_url}
                              alt={result.title}
                              style={{
                                width: "100%",
                                height: window.innerWidth < 768 ? "192px" : "100%",
                                objectFit: "cover",
                                display: "block"
                              }}
                            />
                            <div style={{
                              position: "absolute",
                              inset: 0,
                              backgroundColor: "rgba(0,0,0,0)",
                              display: "flex",
                              alignItems: "center",
                              justifyContent: "center",
                              transition: "all 0.3s"
                            }}
                            onMouseEnter={(e) => {
                              e.currentTarget.style.backgroundColor = "rgba(0,0,0,0.3)";
                              e.currentTarget.querySelector('svg').style.opacity = "1";
                            }}
                            onMouseLeave={(e) => {
                              e.currentTarget.style.backgroundColor = "rgba(0,0,0,0)";
                              e.currentTarget.querySelector('svg').style.opacity = "0";
                            }}>
                              <svg style={{ width: "64px", height: "64px", color: "#ffffff", opacity: 0, transition: "opacity 0.3s" }} fill="currentColor" viewBox="0 0 24 24">
                                <path d="M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z"/>
                              </svg>
                            </div>
                          </a>
                        </div>

                        {/* Content */}
                        <div style={{ flex: 1, padding: "24px" }}>
                          <div style={{
                            display: "flex",
                            alignItems: "flex-start",
                            justifyContent: "space-between",
                            gap: "16px",
                            marginBottom: "12px"
                          }}>
                            <div style={{ flex: 1 }}>
                              <div style={{ display: "flex", alignItems: "center", gap: "12px", marginBottom: "8px" }}>
                                <span style={{
                                  display: "flex",
                                  alignItems: "center",
                                  justifyContent: "center",
                                  width: "32px",
                                  height: "32px",
                                  backgroundColor: "#2563eb",
                                  color: "#ffffff",
                                  fontWeight: "700",
                                  borderRadius: "50%",
                                  fontSize: "14px"
                                }}>
                                  {result.rank || index + 1}
                                </span>
                                <h3 style={{
                                  fontSize: "20px",
                                  fontWeight: "700",
                                  color: "#0f172a",
                                  margin: 0,
                                  lineHeight: "1.4"
                                }}>
                                  {result.title}
                                </h3>
                              </div>
                              <p style={{
                                display: "flex",
                                alignItems: "center",
                                gap: "8px",
                                color: "#64748b",
                                fontSize: "14px",
                                margin: 0
                              }}>
                                <svg style={{ width: "16px", height: "16px" }} fill="currentColor" viewBox="0 0 24 24">
                                  <path d="M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z"/>
                                </svg>
                                {result.channel_title || result.channel}
                              </p>
                            </div>

                            <div style={{
                              padding: "6px 12px",
                              borderRadius: "9999px",
                              fontSize: "13px",
                              fontWeight: "600",
                              color: getSimilarityColor(result.similarity),
                              backgroundColor: getSimilarityBgColor(result.similarity)
                            }}>
                              {((result.similarity || 0) * 100).toFixed(1)}% match
                            </div>
                          </div>
<p style={{ color: "#64748b", fontSize: "13px", margin: "2px 0 0 0", display: "flex", alignItems: "center", gap: "4px" }}>
  📊 SimilarityScore: {(result.similarity || 0).toFixed(2)}
</p>



                          <div style={{ display: "flex", alignItems: "center", gap: "16px", marginTop: "16px" }}>
                            <a
                              href={result.video_url}
                              target="_blank"
                              rel="noopener noreferrer"
                              style={{
                                display: "inline-flex",
                                alignItems: "center",
                                gap: "8px",
                                padding: "10px 16px",
                                backgroundColor: "#dc2626",
                                color: "#ffffff",
                                fontWeight: "600",
                                fontSize: "14px",
                                borderRadius: "8px",
                                textDecoration: "none",
                                transition: "all 0.3s"
                              }}
                              onMouseEnter={(e) => {
                                e.target.style.backgroundColor = "#b91c1c";
                              }}
                              onMouseLeave={(e) => {
                                e.target.style.backgroundColor = "#dc2626";
                              }}
                            >
                              <svg style={{ width: "16px", height: "16px" }} fill="currentColor" viewBox="0 0 24 24">
                                <path d="M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z"/>
                              </svg>
                              Watch on YouTube
                              <svg style={{ width: "12px", height: "12px" }} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                              </svg>
                            </a>

                            
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </>
            ) : (
              <div style={{
                textAlign: "center",
                padding: "48px",
                backgroundColor: "#ffffff",
                borderRadius: "12px",
                boxShadow: "0 4px 12px rgba(0,0,0,0.08)"
              }}>
                <svg style={{ width: "64px", height: "64px", color: "#cbd5e1", margin: "0 auto 16px" }} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
                <h3 style={{ fontSize: "20px", fontWeight: "600", color: "#475569", margin: "0 0 8px 0" }}>
                  No results found
                </h3>
                <p style={{ color: "#94a3b8", margin: 0 }}>
                  Try adjusting your search query or using different keywords
                </p>
              </div>
            )}
          </div>
        )}

        {/* Initial State */}
        {!searched && !loading && (
          <div style={{ textAlign: "center", padding: "64px 20px" }}>
            <div style={{
              display: "inline-block",
              padding: "16px",
              backgroundColor: "#dbeafe",
              borderRadius: "50%",
              marginBottom: "16px"
            }}>
              <svg style={{ width: "48px", height: "48px", color: "#2563eb" }} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
            </div>
            <h3 style={{ fontSize: "24px", fontWeight: "700", color: "#0f172a", margin: "0 0 8px 0" }}>
              Start Your Semantic Search
            </h3>
            <p style={{
              color: "#64748b",
              maxWidth: "672px",
              margin: "0 auto",
              fontSize: "16px",
              lineHeight: "1.6"
            }}>
              Enter a natural language query to find relevant YouTube videos. Our AI-powered semantic search
              understands the meaning behind your words to deliver the most relevant results.
            </p>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer style={{
        marginTop: "64px",
        padding: "32px 20px",
        borderTop: "1px solid #e2e8f0",
        backgroundColor: "#ffffff"
      }}>
        <div style={{
          maxWidth: "1280px",
          margin: "0 auto",
          textAlign: "center",
          color: "#64748b"
        }}>
          <p style={{ margin: 0 }}>Powered by Sentence Transformers & ChromaDB</p>
        </div>
      </footer>

      <style>{`
        @keyframes spin {
          to { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
}

export default App;