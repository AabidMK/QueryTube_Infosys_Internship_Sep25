import React from "react";
import { motion, AnimatePresence } from "framer-motion";
import { X } from "lucide-react";

const CategoryChips = ({ options = [], selected = [], onChange }) => {
  const toggle = (opt) => {
    const next = selected.includes(opt) 
      ? selected.filter((s) => s !== opt) 
      : [...selected, opt];
    onChange(next);
  };

  if (options.length === 0) return null;

  return (
    <div className="flex flex-wrap items-center gap-2">
      <AnimatePresence>
        {options.map((opt, index) => {
          const active = selected.includes(opt);
          return (
            <motion.button
              key={opt}
              onClick={() => toggle(opt)}
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: index * 0.05 }}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              title={`Filter by ${opt}`}
              className={`
                group relative px-4 py-2 text-sm font-medium rounded-full border-2 
                transition-all duration-300 shadow-sm hover:shadow-md
                ${
                  active
                    ? "bg-gradient-to-r from-blue-600 to-purple-600 text-white border-transparent shadow-blue-500/50"
                    : "bg-white dark:bg-slate-800 text-gray-700 dark:text-gray-300 border-gray-200 dark:border-slate-700 hover:border-blue-500 dark:hover:border-purple-500"
                }
              `}
            >
              <span className="flex items-center gap-1.5">
                {opt.charAt(0).toUpperCase() + opt.slice(1)}
                {active && (
                  <motion.span
                    initial={{ opacity: 0, scale: 0 }}
                    animate={{ opacity: 1, scale: 1 }}
                    exit={{ opacity: 0, scale: 0 }}
                  >
                    <X className="w-3.5 h-3.5" />
                  </motion.span>
                )}
              </span>
              
              {/* Active Indicator Dot */}
              {active && (
                <motion.span
                  layoutId="activeIndicator"
                  className="absolute -top-1 -right-1 w-3 h-3 bg-green-400 rounded-full border-2 border-white dark:border-slate-900"
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  transition={{ type: "spring", stiffness: 500, damping: 30 }}
                />
              )}
            </motion.button>
          );
        })}
        
        {/* Clear All Button */}
        {selected.length > 0 && (
          <motion.button
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.8 }}
            onClick={() => onChange([])}
            className="px-3 py-1.5 text-xs font-medium text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-full transition-colors"
          >
            Clear Filters
          </motion.button>
        )}
      </AnimatePresence>
    </div>
  );
};

export default CategoryChips;
