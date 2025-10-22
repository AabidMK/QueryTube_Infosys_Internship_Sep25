import React from "react";
import { X, Search, Filter, Zap, Target, BookOpen } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

const HelpModal = ({ open = false, onClose = () => {} }) => {
  const features = [
    {
      icon: Search,
      title: "Natural Language Search",
      description: "Write queries as natural sentences. Try 'Explain transformers simply' or 'Best Python tutorials for data science'.",
      color: "text-blue-600 dark:text-blue-400 bg-blue-100 dark:bg-blue-900/30"
    },
    {
      icon: Target,
      title: "Semantic Understanding",
      description: "Our AI understands context and meaning, not just keywords. Get relevant results based on what you actually mean.",
      color: "text-purple-600 dark:text-purple-400 bg-purple-100 dark:bg-purple-900/30"
    },
    {
      icon: Filter,
      title: "Category Filters",
      description: "Toggle categories to narrow your search. Combine multiple filters for more precise results.",
      color: "text-green-600 dark:text-green-400 bg-green-100 dark:bg-green-900/30"
    },
    {
      icon: Zap,
      title: "Smart Ranking",
      description: "Results are ranked by similarity score, telling you exactly how relevant the video content is to your query.",
      color: "text-yellow-600 dark:text-yellow-400 bg-yellow-100 dark:bg-yellow-900/30"
    },
  ];

  const modalVariants = {
    hidden: { opacity: 0, scale: 0.8, y: 50 },
    visible: { opacity: 1, scale: 1, y: 0, transition: { type: "spring", stiffness: 300, damping: 30 } },
    exit: { opacity: 0, scale: 0.8, y: 50 }
  };

  return (
    <AnimatePresence>
      {open && (
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
            className="fixed inset-0 bg-black bg-opacity-50 dark:bg-opacity-70 z-40 transition-opacity"
          />

          {/* Modal */}
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
            <motion.div
              variants={modalVariants}
              initial="hidden"
              animate="visible"
              exit="exit"
              className="bg-white dark:bg-slate-900 rounded-2xl shadow-2xl w-full max-w-lg max-h-[90vh] flex flex-col overflow-hidden"
            >
              {/* Header */}
              <div className="sticky top-0 bg-white dark:bg-slate-900 p-6 border-b border-gray-200 dark:border-slate-700 flex items-center justify-between">
                <div className="flex items-center gap-3">
                    <BookOpen className="w-6 h-6 text-blue-600 dark:text-purple-400" />
                    <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-100">
                        How Semantic Search Works
                    </h2>
                </div>
                <button
                  onClick={onClose}
                  className="p-2 rounded-full hover:bg-gray-100 dark:hover:bg-slate-800 transition"
                  title="Close"
                >
                  <X className="w-6 h-6 text-gray-500" />
                </button>
              </div>

              {/* Content */}
              <div className="p-6 overflow-y-auto flex-grow">
                <p className="text-gray-700 dark:text-gray-300 mb-6 border-l-4 border-blue-500 pl-4 py-1 bg-blue-50 dark:bg-blue-900/10 rounded-r-lg">
                    Semantic search uses **vector embeddings** to understand the meaning and context of your query, instead of relying on exact keyword matches.
                </p>

                <div className="grid grid-cols-1 gap-4 mb-8">
                  {features.map((feature, index) => (
                    <motion.div
                      key={index}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: index * 0.1 }}
                      className="flex items-start gap-4 p-4 rounded-xl border border-gray-200 dark:border-slate-700 bg-gray-50 dark:bg-slate-800"
                    >
                      <div className={`p-3 rounded-full ${feature.color} flex-shrink-0`}>
                        <feature.icon className="w-5 h-5" />
                      </div>
                      <div>
                        <h3 className="font-semibold text-gray-900 dark:text-gray-100 mb-1">{feature.title}</h3>
                        <p className="text-sm text-gray-600 dark:text-gray-400">{feature.description}</p>
                      </div>
                    </motion.div>
                  ))}
                </div>

                <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: 0.5 }}
                >
                  <h3 className="text-xl font-bold text-gray-900 dark:text-gray-100 mb-3">Tips for Best Results</h3>
                  <ul className="space-y-2 text-gray-700 dark:text-gray-300">
                    <li className="flex items-start gap-2">
                      <span className="text-blue-600 dark:text-blue-400 font-bold">•</span>
                      <span>Use full sentences for complex ideas (e.g., "What are the latest advances in neural network optimization?")</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <span className="text-green-600 dark:text-green-400 font-bold">•</span>
                      <span>Combine categories to find exactly what you need</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <span className="text-red-600 dark:text-red-400 font-bold">•</span>
                      <span>Check the match percentage to find the most relevant videos</span>
                    </li>
                  </ul>
                </motion.div>
              </div>

              {/* Footer */}
              <div className="sticky bottom-0 bg-gray-50 dark:bg-slate-800 px-6 py-4 border-t border-gray-200 dark:border-slate-700">
                <div className="flex items-center justify-between">
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    Need more help? Contact support or check our documentation.
                  </p>
                  <button
                    onClick={onClose}
                    className="px-5 py-2 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg font-medium hover:from-blue-700 hover:to-purple-700 transition-all shadow-md hover:shadow-lg"
                  >
                    Got it!
                  </button>
                </div>
              </div>
            </motion.div>
          </div>
        </>
      )}
    </AnimatePresence>
  );
};

export default HelpModal;
