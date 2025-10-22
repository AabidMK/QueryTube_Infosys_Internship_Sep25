import { useState, useEffect } from "react";
import axios from "axios";
import { motion, AnimatePresence } from "framer-motion";
import Navbar from "./components/Navbar";
import SearchBar from "./components/SearchBar";
import VideoCard from "./components/VideoCard";
import ParticlesBg from "./components/ParticlesBg";
import Sidebar from "./components/Sidebar";
import { Loader2 } from "lucide-react";

const App = () => {
  const [query, setQuery] = useState("");
  const [videos, setVideos] = useState([]);
  const [loading, setLoading] = useState(false);
  const [sortBy, setSortBy] = useState("similarity");
  const [darkMode, setDarkMode] = useState(true);
  const [recentSearches, setRecentSearches] = useState([]);
  const [sidebarOpen, setSidebarOpen] = useState(true);

  useEffect(() => {
    const saved = localStorage.getItem("recentSearches");
    if (saved) setRecentSearches(JSON.parse(saved));
  }, []);

  const handleSearch = async (q = query) => {
    if (!q.trim()) return;
    setQuery(q);
    setLoading(true);
    setVideos([]);

    try {
      const res = await axios.post("http://127.0.0.1:8000/search", { query: q });
      let sorted = res.data;

      if (sortBy === "channel") {
        sorted = sorted.sort((a, b) =>
          a.channel_title.localeCompare(b.channel_title)
        );
      } else {
        sorted = sorted.sort((a, b) => b.similarity_score - a.similarity_score);
      }

      setVideos(sorted);
      const updated = [q, ...recentSearches.filter((s) => s !== q)].slice(0, 5);
      setRecentSearches(updated);
      localStorage.setItem("recentSearches", JSON.stringify(updated));
    } catch (err) {
      console.error("❌ Error fetching videos:", err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      className={`min-h-screen flex transition-colors duration-700 ${
        darkMode
          ? "bg-gradient-to-br from-gray-900 via-gray-800 to-black text-white"
          : "bg-gradient-to-br from-gray-50 via-gray-100 to-gray-200 text-gray-900"
      }`}
    >
      <ParticlesBg darkMode={darkMode} />

      {/* Animated Sidebar Drawer */}
      <AnimatePresence>
        {sidebarOpen && (
          <motion.div
            initial={{ x: -250, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            exit={{ x: -250, opacity: 0 }}
            transition={{ duration: 0.4, ease: "easeInOut" }}
            className="fixed top-0 left-0 h-full z-40"
          >
            <Sidebar
              recentSearches={recentSearches}
              onSearch={handleSearch}
              darkMode={darkMode}
              sidebarOpen={sidebarOpen}
              setSidebarOpen={setSidebarOpen}
            />
          </motion.div>
        )}
      </AnimatePresence>

      {/* Main Section */}
      <div
        className={`flex-1 transition-all duration-500 ${
          sidebarOpen ? "ml-64" : "ml-10"
        }`}
      >
        <Navbar darkMode={darkMode} setDarkMode={setDarkMode} />

        <main className="relative container mx-auto px-4 py-10 mt-20 z-10">
          <motion.h1
            className="text-5xl md:text-6xl font-extrabold text-center mb-10 bg-gradient-to-r from-fuchsia-500 via-blue-500 to-cyan-400 bg-clip-text text-transparent drop-shadow-lg"
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
          >
            YouTube Search Engine
          </motion.h1>

          <SearchBar
            query={query}
            setQuery={setQuery}
            onSearch={handleSearch}
            sortBy={sortBy}
            setSortBy={setSortBy}
          />

          {loading ? (
            <div className="flex justify-center items-center mt-20">
              <Loader2 className="animate-spin text-blue-400 w-14 h-14" />
            </div>
          ) : (
            <motion.div
              className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-8 mt-10"
              initial="hidden"
              animate="visible"
              variants={{
                hidden: { opacity: 0 },
                visible: {
                  opacity: 1,
                  transition: { staggerChildren: 0.1 },
                },
              }}
            >
              {videos.map((video, i) => (
                <VideoCard key={i} video={video} />
              ))}
            </motion.div>
          )}
        </main>
      </div>
    </div>
  );
};

export default App;
