import { Search } from "lucide-react";

const SearchBar = ({ query, setQuery, onSearch, sortBy, setSortBy }) => {
  const handleKeyPress = (e) => {
    if (e.key === "Enter") onSearch();
  };

  return (
    <div className="flex flex-col md:flex-row gap-4 justify-center items-center mt-28">
      <div className="relative w-full md:w-1/2">
        <input
          type="text"
          placeholder="Search videos..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={handleKeyPress}
          className="w-full px-5 py-3 rounded-2xl border border-gray-300 dark:border-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white/80 dark:bg-gray-800/70 backdrop-blur text-lg shadow-sm"
        />
        <Search
          onClick={onSearch}
          className="absolute right-4 top-3.5 text-gray-500 hover:text-blue-500 cursor-pointer"
        />
      </div>

      <select
        value={sortBy}
        onChange={(e) => setSortBy(e.target.value)}
        className="px-4 py-3 rounded-2xl bg-white/80 dark:bg-gray-800/70 backdrop-blur border dark:border-gray-700 text-gray-800 dark:text-gray-200 shadow-sm"
      >
        <option value="similarity">Sort by Similarity</option>
        <option value="channel">Sort by Channel</option>
      </select>
    </div>
  );
};

export default SearchBar;
