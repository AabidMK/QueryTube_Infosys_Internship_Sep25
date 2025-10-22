import { useEffect, useState } from "react";
import { Sun, Moon } from "lucide-react";

const ThemeToggle = () => {
  const [darkMode, setDarkMode] = useState(
    localStorage.getItem("theme") === "dark"
  );

  useEffect(() => {
    if (darkMode) {
      document.documentElement.classList.add("dark");
      localStorage.setItem("theme", "dark");
    } else {
      document.documentElement.classList.remove("dark");
      localStorage.setItem("theme", "light");
    }
  }, [darkMode]);

  return (
    <button
      onClick={() => setDarkMode(!darkMode)}
      className="p-2 rounded-full bg-indigo-500/20 hover:bg-indigo-500/40 transition-all duration-300"
    >
      {darkMode ? (
        <Sun className="text-yellow-400" size={22} />
      ) : (
        <Moon className="text-indigo-400" size={22} />
      )}
    </button>
  );
};

export default ThemeToggle;
