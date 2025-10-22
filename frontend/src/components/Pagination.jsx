import React from "react";
import { ChevronLeft, ChevronRight, ChevronsLeft, ChevronsRight } from "lucide-react";
import { motion } from "framer-motion";

const Pagination = ({ current = 1, pageSize = 10, total = 0, onPageChange }) => {
  const totalPages = Math.max(1, Math.ceil((total || 0) / pageSize));
  
  const goToPage = (page) => {
    if (page >= 1 && page <= totalPages) {
      onPageChange(page);
    }
  };

  const getPageNumbers = () => {
    const pages = [];
    const showPages = 5; // Number of page buttons to show
    
    if (totalPages <= showPages) {
      for (let i = 1; i <= totalPages; i++) {
        pages.push(i);
      }
    } else {
      if (current <= 3) {
        for (let i = 1; i <= 4; i++) pages.push(i);
        pages.push('...');
        pages.push(totalPages);
      } else if (current >= totalPages - 2) {
        pages.push(1);
        pages.push('...');
        for (let i = totalPages - 3; i <= totalPages; i++) pages.push(i);
      } else {
        pages.push(1);
        pages.push('...');
        for (let i = current - 1; i <= current + 1; i++) pages.push(i);
        pages.push('...');
        pages.push(totalPages);
      }
    }
    return pages;
  };

  if (totalPages <= 1) return null;

  return (
    <div className="flex items-center justify-center space-x-2 my-8">
      {/* First Page */}
      <button
        onClick={() => goToPage(1)}
        disabled={current === 1}
        className="p-2 rounded-lg border border-gray-300 dark:border-slate-600 bg-white dark:bg-slate-800 hover:bg-gray-50 dark:hover:bg-slate-700 disabled:opacity-40 disabled:cursor-not-allowed transition-all"
        title="First page"
      >
        <ChevronsLeft className="w-4 h-4" />
      </button>

      {/* Previous Page */}
      <button
        onClick={() => goToPage(current - 1)}
        disabled={current === 1}
        className="flex items-center gap-1 px-3 py-2 rounded-lg border border-gray-300 dark:border-slate-600 bg-white dark:bg-slate-800 hover:bg-gray-50 dark:hover:bg-slate-700 disabled:opacity-40 disabled:cursor-not-allowed transition-all"
        title="Previous page"
      >
        <ChevronLeft className="w-4 h-4" />
        <span className="text-sm font-medium hidden sm:inline">Prev</span>
      </button>

      {/* Page Numbers */}
      <div className="hidden sm:flex items-center space-x-1">
        {getPageNumbers().map((page, index) => {
          if (page === '...') {
            return (
              <span key={index} className="px-3 py-2 text-gray-500 dark:text-gray-400">
                ...
              </span>
            );
          }
          
          const active = page === current;
          return (
            <motion.button
              key={index}
              onClick={() => goToPage(page)}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              className={`
                px-4 py-2 text-sm font-medium rounded-lg transition-all relative
                ${active 
                  ? 'bg-gradient-to-r from-blue-600 to-purple-600 text-white shadow-md'
                  : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-slate-700'
                }
              `}
            >
              {page}
            </motion.button>
          );
        })}
      </div>

      {/* Current Page Indicator (Mobile) */}
      <div className="sm:hidden px-4 py-2 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg text-sm font-medium">
        Page {current} of {totalPages}
      </div>

      {/* Next Page */}
      <button
        onClick={() => goToPage(current + 1)}
        disabled={current >= totalPages}
        className="flex items-center gap-1 px-3 py-2 rounded-lg border border-gray-300 dark:border-slate-600 bg-white dark:bg-slate-800 hover:bg-gray-50 dark:hover:bg-slate-700 disabled:opacity-40 disabled:cursor-not-allowed transition-all"
        title="Next page"
      >
        <span className="text-sm font-medium hidden sm:inline">Next</span>
        <ChevronRight className="w-4 h-4" />
      </button>

      {/* Last Page */}
      <button
        onClick={() => goToPage(totalPages)}
        disabled={current >= totalPages}
        className="p-2 rounded-lg border border-gray-300 dark:border-slate-600 bg-white dark:bg-slate-800 hover:bg-gray-50 dark:hover:bg-slate-700 disabled:opacity-40 disabled:cursor-not-allowed transition-all"
        title="Last page"
      >
        <ChevronsRight className="w-4 h-4" />
      </button>
    </div>
  );
};

export default Pagination;
