import React, { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";

const Tooltip = ({ children, text, placement = "top", delay = 0 }) => {
  const [isVisible, setIsVisible] = useState(false);

  const getPositionClasses = () => {
    switch (placement) {
      case "top":
        return "-top-10 left-1/2 -translate-x-1/2";
      case "bottom":
        return "-bottom-10 left-1/2 -translate-x-1/2";
      case "left":
        return "top-1/2 -translate-y-1/2 -left-full mr-2";
      case "right":
        return "top-1/2 -translate-y-1/2 -right-full ml-2";
      default:
        return "-top-10 left-1/2 -translate-x-1/2";
    }
  };

  const getArrowClasses = () => {
    switch (placement) {
      case "top":
        return "bottom-0 left-1/2 -translate-x-1/2 translate-y-1/2 rotate-45";
      case "bottom":
        return "top-0 left-1/2 -translate-x-1/2 -translate-y-1/2 rotate-45";
      case "left":
        return "right-0 top-1/2 -translate-y-1/2 translate-x-1/2 rotate-45";
      case "right":
        return "left-0 top-1/2 -translate-y-1/2 -translate-x-1/2 rotate-45";
      default:
        return "bottom-0 left-1/2 -translate-x-1/2 translate-y-1/2 rotate-45";
    }
  };

  return (
    <div
      className="relative inline-block"
      onMouseEnter={() => setIsVisible(true)}
      onMouseLeave={() => setIsVisible(false)}
      onFocus={() => setIsVisible(true)}
      onBlur={() => setIsVisible(false)}
    >
      {children}
      
      <AnimatePresence>
        {isVisible && text && (
          <motion.div
            initial={{ opacity: 0, scale: 0.95, y: placement === "top" ? 5 : placement === "bottom" ? -5 : 0 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: placement === "top" ? 5 : placement === "bottom" ? -5 : 0 }}
            transition={{ duration: 0.15, delay }}
            className={`absolute z-50 pointer-events-none ${getPositionClasses()}`}
          >
            <div className="relative">
              {/* Tooltip Content */}
              <div className="bg-gray-900 dark:bg-gray-800 text-white text-xs px-3 py-1.5 rounded-lg shadow-xl whitespace-nowrap">
                {text}
              </div>
              {/* Arrow */}
              <div
                className={`absolute w-3 h-3 bg-gray-900 dark:bg-gray-800 ${getArrowClasses()}`}
              />
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default Tooltip;
