import { motion } from "framer-motion";
import { ExternalLink, Star } from "lucide-react";

const VideoCard = ({ video }) => {
  return (
    <motion.div
      whileHover={{ y: -6, scale: 1.02 }}
      transition={{ duration: 0.25, ease: "easeOut" }}
      className="relative bg-white/80 dark:bg-gray-800/80 backdrop-blur-lg 
                 p-5 rounded-2xl shadow-lg hover:shadow-2xl 
                 border border-gray-200 dark:border-gray-700 
                 overflow-hidden transition-all duration-300"
    >
      {/* Thumbnail */}
      <div className="relative">
        <img
          src={video.thumbnail}
          alt={video.video_title}
          className="w-full h-52 object-cover rounded-xl mb-4 
                     transition-transform duration-500 hover:scale-[1.03]"
          loading="lazy"
        />
        <div className="absolute inset-0 bg-gradient-to-t 
                        from-black/60 via-transparent to-transparent 
                        rounded-xl opacity-0 hover:opacity-100 
                        transition-opacity duration-300 flex items-end justify-between p-3">
          <span className="text-sm text-white font-medium">
            {video.channel_title}
          </span>
        </div>
      </div>

      {/* Title */}
      <h3 className="text-lg font-semibold mb-2 text-transparent 
                     bg-clip-text bg-gradient-to-r from-blue-600 to-purple-600 
                     dark:from-indigo-400 dark:to-pink-400 
                     line-clamp-2 leading-tight">
        {video.video_title}
      </h3>

      {/* Description */}
      <p className="text-gray-600 dark:text-gray-300 text-sm mb-4 line-clamp-3">
        {video.description}
      </p>

      {/* Footer: Buttons and Similarity */}
      <div className="flex justify-between items-center">
        <a
          href={video.yt_link}
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex items-center gap-2 px-4 py-2 
                     bg-gradient-to-r from-blue-600 to-purple-600 
                     text-white font-medium text-sm rounded-xl 
                     shadow-md hover:shadow-lg hover:scale-105 transition-all duration-200"
        >
          Watch on YouTube <ExternalLink size={16} />
        </a>

        <div
          className="flex items-center gap-1 text-xs px-3 py-1 rounded-full 
                     bg-yellow-100 dark:bg-yellow-500/20 
                     text-yellow-700 dark:text-yellow-300 font-semibold"
        >
          <Star size={14} />
          {video.similarity_score?.toFixed(3)}
        </div>
      </div>
    </motion.div>
  );
};

export default VideoCard;
