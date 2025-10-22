import { useState, useEffect } from "react";
import { Search, X, Sparkles } from "lucide-react";
import { motion } from "framer-motion";

const SearchBar = ({ onSearch, isLoading }) => {
  const [query, setQuery] = useState("");
  const [isFocused, setIsFocused] = useState(false);

  useEffect(() => {
    const last = localStorage.getItem("lastQuery") || "";
    setQuery(last);
  }, []);

  const handleSubmit = (e) => {
    e && e.preventDefault();
    const q = query.trim();
    if (!q) return;
    localStorage.setItem("lastQuery", q);
    onSearch(q);
  };

  const clear = () => {
    setQuery("");
    localStorage.removeItem("lastQuery");
  };

  const onKey = (e) => {
    if (e.key === "Enter") handleSubmit();
  };

  const suggestions = [
    "Explain quantum computing simply",
    "Best AI tutorials for beginners",
    "How does machine learning work",
    "Data science career advice"
  ];

  return (
    <motion.div
      initial={{ opacity: 0, y: -10 }}
      animate={{ opacity: 1, y: 0 }}
      className="w-full"
    >
      <form onSubmit={handleSubmit} className="relative">
        <div className={`relative transition-all duration-300 rounded-xl shadow-xl border-2 ${isFocused ? 'border-blue-500 dark:border-purple-500' : 'border-gray-200 dark:border-slate-700'}`}>
          
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onFocus={() => setIsFocused(true)}
            onBlur={() => setIsFocused(false)}
            onKeyUp={onKey}
            placeholder="Search videos using natural language..."
            className="w-full pl-5 pr-24 py-4 text-lg bg-white dark:bg-slate-800 text-gray-800 dark:text-gray-100 rounded-xl focus:outline-none placeholder-gray-500 dark:placeholder-gray-400"
            disabled={isLoading}
          />

          <div className="absolute inset-y-0 right-0 flex items-center pr-2">
            
            {query.length > 0 && !isLoading && (
              <motion.button
                type="button"
                onClick={clear}
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.8 }}
                className="p-2 mr-1 text-gray-500 hover:text-red-500 dark:text-gray-400 dark:hover:text-red-400 rounded-full transition-colors"
                title="Clear search"
              >
                <X className="w-5 h-5" />
              </motion.button>
            )}

            <button
              type="submit"
              disabled={isLoading || !query.trim()}
              className={`
                px-4 py-2.5 rounded-lg font-semibold text-white transition-all duration-300 flex items-center gap-2 
                ${isLoading || !query.trim()
                  ? "bg-gray-400 dark:bg-slate-600 cursor-not-allowed"
                  : "bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 shadow-lg shadow-blue-500/50"
                }
              `}
              title="Perform search"
            >
              {isLoading ? (
                <div className="flex items-center gap-2">
                  <svg className="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  <span>Searching...</span>
                </div>
              ) : (
                <>
                  <Search className="w-5 h-5" />
                  <span className="hidden sm:inline">Search</span>
                </>
              )}
            </button>
          </div>
        </div>
      </form>

      {/* Search Suggestions */}
      {!query && !isLoading && (
        <motion.div
          initial={{ opacity: 0, y: -5 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="mt-4 flex flex-wrap items-center gap-2"
        >
          <div className="flex items-center gap-2 text-sm text-gray-500 dark:text-gray-400">
            <Sparkles className="w-4 h-4 text-yellow-500" />
            <span className="font-medium">Try:</span>
          </div>
          {suggestions.map((suggestion, i) => (
            <motion.button
              key={i}
              onClick={() => {
                setQuery(suggestion);
                localStorage.setItem("lastQuery", suggestion);
                onSearch(suggestion);
              }}
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: i * 0.05 }}
              className="px-3 py-1.5 text-sm bg-white dark:bg-slate-800 border border-gray-200 dark:border-slate-700 rounded-full hover:border-blue-500 dark:hover:border-purple-500 hover:bg-blue-50 dark:hover:bg-purple-900/20 text-gray-700 dark:text-gray-300 transition-colors"
            >
              {suggestion}
            </motion.button>
          ))}
        </motion.div>
      )}
    </motion.div>
  );
};

export default SearchBar;
