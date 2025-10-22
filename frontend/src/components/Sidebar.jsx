import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Menu, X, Clock } from "lucide-react";

const Sidebar = ({ recentSearches, onSearch, darkMode }) => {
  const [isOpen, setIsOpen] = useState(true);

  return (
    <>
      {/* Sidebar */}
      <AnimatePresence>
        {isOpen && (
          <motion.aside
            initial={{ x: -250, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            exit={{ x: -250, opacity: 0 }}
            transition={{ duration: 0.4, ease: "easeInOut" }}
            className={`fixed top-0 left-0 h-full w-64 p-5 z-30 shadow-xl backdrop-blur-lg
              ${darkMode ? "bg-gray-900/80 border-gray-700" : "bg-white/80 border-gray-200"}
              border-r`}
          >
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-lg font-bold tracking-wide bg-gradient-to-r from-pink-500 to-purple-500 bg-clip-text text-transparent">
                Recent Searches
              </h2>
              <button
                onClick={() => setIsOpen(false)}
                className="p-2 hover:bg-gray-700/30 rounded-full transition"
              >
                <X size={22} />
              </button>
            </div>

            <div className="space-y-3">
              {recentSearches.length === 0 ? (
                <p className="text-sm opacity-60">No recent searches yet</p>
              ) : (
                recentSearches.map((search, i) => (
                  <motion.button
                    key={i}
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.97 }}
                    onClick={() => onSearch(search)}
                    className={`flex items-center gap-2 w-full text-left px-3 py-2 rounded-lg transition
                      ${darkMode ? "hover:bg-gray-800" : "hover:bg-gray-100"}`}
                  >
                    <Clock size={16} className="text-purple-400" />
                    <span>{search}</span>
                  </motion.button>
                ))
              )}
            </div>
          </motion.aside>
        )}
      </AnimatePresence>

      {/* Floating Toggle Button */}
      {!isOpen && (
        <motion.button
          initial={{ opacity: 0, x: -40 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.2 }}
          onClick={() => setIsOpen(true)}
          className={`fixed top-5 left-5 z-40 p-3 rounded-full shadow-lg backdrop-blur-md 
            border transition-all hover:scale-110 
            ${darkMode 
              ? "bg-gray-900/80 border-gray-700 text-white hover:bg-gray-800/80" 
              : "bg-white/80 border-gray-200 text-gray-800 hover:bg-gray-100/80"
            }`}
        >
          <Menu size={24} />
        </motion.button>
      )}
    </>
  );
};

export default Sidebar;
