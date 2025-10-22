import { useEffect, useState, useMemo } from "react";
import { motion } from "framer-motion";
import { Video, AlertCircle, Info, Sparkles, SlidersHorizontal, ArrowUp, ArrowDown } from "lucide-react";

import SearchBar from "../components/SearchBar";
import ResultCard from "../components/ResultCard";
import Loader from "../components/Loader";
import ThemeToggle from "../components/ThemeToggle";
import Pagination from "../components/Pagination";
import HelpModal from "../components/HelpModal";

import { searchVideos } from "../api/searchApi";

// Sorting Options
const SORT_OPTIONS = [
  { key: "similarity_score", label: "Best Match", type: "number", defaultDirection: "desc" },
  { key: "rank", label: "Rank", type: "number", defaultDirection: "asc" },
  { key: "view_count", label: "Views", type: "number", defaultDirection: "desc" },
  { key: "like_count", label: "Likes", type: "number", defaultDirection: "desc" },
  { key: "published_at", label: "Newest", type: "date", defaultDirection: "desc" },
  { key: "duration", label: "Duration", type: "number", defaultDirection: "asc" },
];

const Home = () => {
  const [results, setResults] = useState([]);
  const [meta, setMeta] = useState({ page: 1, page_size: 20, total_results: 0 });
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [hasSearched, setHasSearched] = useState(false);
  const [currentQuery, setCurrentQuery] = useState("");

  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(20);
  const [showHelp, setShowHelp] = useState(false);

  // Sorting
  const [sortKey, setSortKey] = useState("similarity_score");
  const [sortDirection, setSortDirection] = useState("desc");

  const sortResults = (data, key, direction) => {
    if (!data || data.length === 0) return [];
    const option = SORT_OPTIONS.find((opt) => opt.key === key);
    if (!option) return data;

    return [...data].sort((a, b) => {
      let valA = a[key];
      let valB = b[key];

      if (option.type === "number") {
        valA = parseFloat(valA) || 0;
        valB = parseFloat(valB) || 0;
      } else if (option.type === "date") {
        valA = new Date(valA || 0).getTime();
        valB = new Date(valB || 0).getTime();
      }

      let comparison = 0;
      if (valA > valB) comparison = 1;
      else if (valA < valB) comparison = -1;

      return direction === "desc" ? comparison * -1 : comparison;
    });
  };

  const sortedResults = useMemo(() => {
    return sortResults(results, sortKey, sortDirection);
  }, [results, sortKey, sortDirection]);

  // Handle Search Execution
  const handleSearch = async (query, p = 1) => {
    if (!query) return;

    if (query !== currentQuery) {
      setPage(1);
      p = 1;
    }

    setCurrentQuery(query);
    setHasSearched(true);
    setIsLoading(true);
    setError(null);
    setResults([]);

    try {
      const response = await searchVideos({
        query,
        page: p,
        page_size: pageSize,
      });

      setResults(response.results || []);
      setMeta({
        page: response.meta.page,
        page_size: response.meta.page_size,
        total_results: response.meta.total_results,
      });

      // persist last query
      try {
        localStorage.setItem("lastQuery", query);
      } catch {}
    } catch (err) {
      console.error("Search failed:", err);
      setError("An error occurred while fetching search results. Please try again.");
    } finally {
      setIsLoading(false);
    }
  };

  const handlePageChange = (newPage) => {
    setPage(newPage);
    handleSearch(currentQuery, newPage);
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  const handleSortChange = (newKey) => {
    if (newKey === sortKey) {
      setSortDirection(sortDirection === "asc" ? "desc" : "asc");
    } else {
      setSortKey(newKey);
      const defaultDirection = SORT_OPTIONS.find((opt) => opt.key === newKey)?.defaultDirection || "desc";
      setSortDirection(defaultDirection);
    }
  };

  useEffect(() => {
    // Load last query if available
    const lastQuery = localStorage.getItem("lastQuery");
    if (lastQuery) {
      setCurrentQuery(lastQuery);
    }
  }, []);

  const renderContent = () => {
    if (isLoading) return <Loader />;

    if (error) {
      return (
        <div className="text-center p-10 bg-red-50 dark:bg-red-900/20 rounded-xl border border-red-200 dark:border-red-800 shadow-lg">
          <AlertCircle className="w-10 h-10 text-red-600 mx-auto mb-4" />
          <p className="text-xl font-semibold text-red-700 dark:text-red-400">{error}</p>
          <p className="text-sm text-red-500 dark:text-red-300 mt-2">Check your network connection or try a different query.</p>
        </div>
      );
    }

    if (hasSearched && sortedResults.length === 0) {
      return (
        <div className="text-center p-10 bg-blue-50 dark:bg-slate-800/50 rounded-xl border border-blue-200 dark:border-slate-700 shadow-lg">
          <Video className="w-10 h-10 text-blue-600 dark:text-blue-400 mx-auto mb-4" />
          <p className="text-xl font-semibold text-blue-700 dark:text-blue-300">No results found.</p>
          <p className="text-sm text-gray-600 dark:text-gray-400 mt-2">Try simplifying your search query or adjusting the filters.</p>
        </div>
      );
    }

    if (sortedResults.length > 0) {
      return (
        <>
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3 }}
            className="flex justify-between items-center mb-6 p-4 bg-white dark:bg-slate-900 rounded-xl shadow-md border border-gray-200 dark:border-slate-700"
          >
            <div className="text-sm font-medium text-gray-700 dark:text-gray-300 flex items-center gap-2">
              <SlidersHorizontal className="w-4 h-4 text-blue-500" />
              Found {meta.total_results.toLocaleString()} results
            </div>

            <div className="flex items-center gap-2">
              <label htmlFor="sort-select" className="text-sm font-medium text-gray-600 dark:text-gray-400 hidden sm:inline">
                Sort by:
              </label>
              <select
                id="sort-select"
                value={sortKey}
                onChange={(e) => handleSortChange(e.target.value)}
                className="p-2 border border-gray-300 dark:border-slate-600 bg-white dark:bg-slate-800 rounded-lg text-sm font-medium text-gray-700 dark:text-gray-300 appearance-none focus:ring-2 focus:ring-blue-500 transition-colors cursor-pointer"
              >
                {SORT_OPTIONS.map((opt) => (
                  <option key={opt.key} value={opt.key}>{opt.label}</option>
                ))}
              </select>

              <motion.button
                onClick={() => setSortDirection(sortDirection === "asc" ? "desc" : "asc")}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className="p-2 rounded-lg bg-gray-100 dark:bg-slate-800 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-slate-700 transition-all border border-gray-300 dark:border-slate-600"
                title={`Change sort direction to ${sortDirection === "asc" ? "Descending" : "Ascending"}`}
              >
                {sortDirection === "asc" ? (
                  <ArrowUp className="w-4 h-4 text-green-500" />
                ) : (
                  <ArrowDown className="w-4 h-4 text-red-500" />
                )}
              </motion.button>
            </div>
          </motion.div>

          <motion.div layout className="grid gap-6">
            {sortedResults.map((result, index) => (
              <ResultCard key={result.video_id} result={result} index={index} />
            ))}
          </motion.div>

          <div className="mt-8 flex justify-center">
            <Pagination
              current={meta.page}
              pageSize={meta.page_size}
              total={meta.total_results}
              onPageChange={handlePageChange}
            />
          </div>
        </>
      );
    }

    // Default landing content
    return (
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        className="text-center p-10 max-w-4xl mx-auto"
      >
        <Sparkles className="w-12 h-12 text-blue-600 dark:text-blue-400 mx-auto mb-6" />
        <h2 className="text-3xl font-bold text-gray-900 dark:text-gray-100 mb-4">
          Discover Videos with AI
        </h2>
        <p className="text-lg text-gray-600 dark:text-gray-400 mb-8">
          Search through video content using semantic understanding.
          <br />
          Find exactly what you're looking for, not just keyword matches.
        </p>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 text-left">
          {[
            { icon: "🔍", title: "Natural Language", desc: "Search using everyday language" },
            { icon: "🎯", title: "Semantic Matching", desc: "Understands context and meaning" },
            { icon: "⚡", title: "Fast Results", desc: "Instant, relevant video discovery" }
          ].map((feature, i) => (
            <div key={i} className="p-4 bg-white dark:bg-slate-900 rounded-xl border border-gray-200 dark:border-slate-700 shadow-lg">
              <div className="text-2xl mb-2">{feature.icon}</div>
              <h3 className="font-semibold text-gray-900 dark:text-gray-100 mb-1">
                {feature.title}
              </h3>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                {feature.desc}
              </p>
            </div>
          ))}
        </div>
      </motion.div>
    );
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-slate-900 transition-colors duration-300">
      <div className="max-w-7xl mx-auto p-4 sm:p-6 lg:p-8">
        <header className="flex flex-col sm:flex-row justify-between items-center mb-8 gap-4">
          <h1 className="text-3xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-purple-600">
            AI Video Search
          </h1>
          <div className="flex items-center gap-3">
            <button
              onClick={() => setShowHelp(true)}
              className="p-2.5 rounded-lg bg-gray-100 dark:bg-slate-800 hover:bg-gray-200 dark:hover:bg-slate-700 transition-colors"
              title="Help & Info"
            >
              <Info className="w-5 h-5 text-blue-500" />
            </button>
            <ThemeToggle />
          </div>
        </header>

        <SearchBar
          onSearch={(query) => handleSearch(query, 1)}
          isLoading={isLoading}
        />

        {hasSearched && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="mt-6 p-4 bg-white dark:bg-slate-900 rounded-xl shadow-md border border-gray-200 dark:border-slate-700"
          >
            <div className="flex justify-between items-center">
              <p className="text-sm text-gray-700 dark:text-gray-300 font-medium">
                Showing results for: <span className="font-bold text-purple-600 dark:text-blue-400">"{currentQuery}"</span>
              </p>
            </div>
          </motion.div>
        )}

        <main className="mt-8">
          {renderContent()}
        </main>
      </div>

      <HelpModal open={showHelp} onClose={() => setShowHelp(false)} />
    </div>
  );
};

export default Home;