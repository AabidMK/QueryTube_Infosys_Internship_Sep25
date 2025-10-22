import { Sun, Moon } from "lucide-react";
import { motion } from "framer-motion";

const Navbar = ({ darkMode, setDarkMode }) => {
  return (
    <motion.nav
      initial={{ y: -60, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.6, ease: "easeOut" }}
      className={`fixed top-0 left-0 w-full z-20 backdrop-blur-lg border-b transition-all
        ${darkMode ? "bg-gray-900/60 border-gray-700" : "bg-white/70 border-gray-200"}
      `}
    >
      <div className="container mx-auto px-6 py-4 flex justify-between items-center">
        {/* Logo */}
        <h1
          className={`text-2xl font-extrabold tracking-wide bg-gradient-to-r 
          from-blue-500 via-purple-500 to-pink-500 bg-clip-text text-transparent`}
        >
          YouTube Search Engine
        </h1>

        {/* Right Section */}
        <div className="flex items-center gap-4">
          {/* Toggle Dark/Light Mode */}
          <motion.button
            whileHover={{ scale: 1.15 }}
            whileTap={{ scale: 0.9 }}
            onClick={() => setDarkMode(!darkMode)}
            className={`p-2 rounded-full transition-all shadow-lg
              ${darkMode
                ? "bg-gray-800 hover:bg-gray-700 text-yellow-400"
                : "bg-gray-100 hover:bg-gray-200 text-gray-700"}
            `}
          >
            {darkMode ? <Sun size={22} /> : <Moon size={22} />}
          </motion.button>
        </div>
      </div>
    </motion.nav>
  );
};

export default Navbar;
