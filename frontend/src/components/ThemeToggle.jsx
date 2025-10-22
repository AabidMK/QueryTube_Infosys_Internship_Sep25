import { useEffect, useState } from "react";
import { Sun, Moon } from "lucide-react";
import { motion } from "framer-motion";

const ThemeToggle = () => {
  const [dark, setDark] = useState(false);
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
    const stored = localStorage.getItem("theme");
    // const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches; // Removed to force default

    // Set default to dark if no theme is stored, or if stored is explicitly 'dark'
    const isInitialDark = stored === "dark" || (!stored);
    
    if (isInitialDark) { 
      setDark(true);
      document.documentElement.classList.add("dark");
    } else {
      setDark(false);
      document.documentElement.classList.remove("dark");
    }
  }, []);

  const toggle = () => {
    const newDark = !dark;
    setDark(newDark);
    
    if (newDark) {
      document.documentElement.classList.add("dark");
      localStorage.setItem("theme", "dark");
    } else {
      document.documentElement.classList.remove("dark");
      localStorage.setItem("theme", "light");
    }
  };

  if (!mounted) {
    return (
      <div className="w-10 h-10 rounded-lg bg-gray-100 dark:bg-slate-800" />
    );
  }

  return (
    <motion.button
      onClick={toggle}
      className="relative w-10 h-10 rounded-lg bg-gray-100 dark:bg-slate-800 hover:bg-gray-200 dark:hover:bg-slate-700 transition-all duration-300 flex items-center justify-center overflow-hidden group"
      whileTap={{ scale: 0.95 }}
      title={dark ? "Switch to light mode" : "Switch to dark mode"}
    >
      {/* Sun Icon (Light Mode) */}
      <motion.div
        initial={false}
        animate={{
          rotate: dark ? 180 : 0,
          scale: dark ? 0 : 1,
          opacity: dark ? 0 : 1,
        }}
        transition={{ duration: 0.3 }}
        className="absolute"
      >
        <Sun className="w-5 h-5 text-yellow-500" />
      </motion.div>

      {/* Moon Icon (Dark Mode) */}
      <motion.div
        initial={false}
        animate={{
          rotate: dark ? 0 : -180,
          scale: dark ? 1 : 0,
          opacity: dark ? 1 : 0,
        }}
        transition={{ duration: 0.3 }}
        className="absolute"
      >
        <Moon className="w-5 h-5 text-slate-400" />
      </motion.div>
    </motion.button>
  );
};

export default ThemeToggle;
