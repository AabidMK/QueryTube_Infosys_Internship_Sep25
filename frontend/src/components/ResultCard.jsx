import { motion } from "framer-motion";
import {
  ExternalLink,
  TrendingUp,
  ThumbsUp,
  Eye,
  Clock,
  Calendar,
  BookOpen,
} from "lucide-react";
import { useState, useEffect } from "react";

const formatCount = (num) => {
  if (num === undefined || num === null) return "N/A";
  const number = Number(num);
  if (number >= 1000000) return (number / 1000000).toFixed(1).replace(/\.0$/, "") + "M";
  if (number >= 1000) return (number / 1000).toFixed(1).replace(/\.0$/, "") + "K";
  return number;
};

const formatDuration = (secondsStr) => {
  if (!secondsStr) return "N/A";
  const seconds = parseFloat(secondsStr);
  if (isNaN(seconds)) return "N/A";
  const h = Math.floor(seconds / 3600);
  const m = Math.floor((seconds % 3600) / 60);
  const s = Math.floor(seconds % 60);
  const mDisplay = String(m).padStart(2, "0");
  const sDisplay = String(s).padStart(2, "0");
  return h > 0 ? `${h}:${mDisplay}:${sDisplay}` : `${mDisplay}:${sDisplay}`;
};

const formatDate = (dateString) => {
  if (!dateString) return "N/A";
  try {
    return new Date(dateString).toLocaleDateString("en-US", {
      year: "numeric",
      month: "short",
      day: "numeric",
    });
  } catch {
    return "N/A";
  }
};

const PLACEHOLDER_IMAGE_URL = (videoId) =>
  `https://placehold.co/480x270/2563eb/ffffff?text=No+Thumbnail+(${videoId})`;

const ResultCard = ({ result }) => {
  if (!result) return null;

  const {
    title,
    video_id,
    channel_title,
    view_count,
    like_count,
    duration,
    published_at,
    similarity_score,
    transcript_preview,
    thumbnail_url,
    thumbnail_default,
    thumbnail_high,
  } = result;

  const youtubeUrl = `https://www.youtube.com/watch?v=${video_id}`;

  // Pick the most reliable thumbnail
  const getThumbnailUrl = () => {
    return (
      thumbnail_url ||
      thumbnail_high ||
      thumbnail_default ||
      `https://i.ytimg.com/vi/${video_id}/hqdefault.jpg`
    );
  };

  const [imageSrc, setImageSrc] = useState(getThumbnailUrl());
  const [hasTriedFallback, setHasTriedFallback] = useState(false);

  useEffect(() => {
    setImageSrc(getThumbnailUrl());
    setHasTriedFallback(false);
  }, [thumbnail_url, thumbnail_high, thumbnail_default, video_id]);

  const handleImageError = () => {
    if (!hasTriedFallback) {
      console.warn(`Thumbnail failed to load for video: ${video_id}, using fallback`);
      setImageSrc(`https://img.youtube.com/vi/${video_id}/mqdefault.jpg`);
      setHasTriedFallback(true);
    } else {
      setImageSrc(PLACEHOLDER_IMAGE_URL(video_id));
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className="bg-white dark:bg-slate-800 p-6 rounded-3xl shadow-xl hover:shadow-2xl transition-all duration-300 border border-gray-100 dark:border-slate-700 flex flex-col md:flex-row gap-6"
    >
      <a
        href={youtubeUrl}
        target="_blank"
        rel="noopener noreferrer"
        className="block flex-shrink-0 w-full md:w-80 rounded-2xl overflow-hidden shadow-lg group relative aspect-video"
        title={`Watch: ${title}`}
      >
        <img
          src={imageSrc?.startsWith("http") ? imageSrc : `https:${imageSrc}`}
          alt={`Thumbnail for ${title}`}
          className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-105"
          loading="lazy"
          onError={handleImageError}
        />
        <div className="absolute inset-0 bg-black bg-opacity-30 group-hover:bg-opacity-10 transition-all duration-300 flex items-center justify-center">
          <Clock className="w-8 h-8 text-white opacity-80 group-hover:opacity-100 transition-opacity" />
        </div>
        <span className="absolute bottom-2 right-2 bg-black/70 text-white text-xs font-semibold px-2 py-0.5 rounded-md">
          {formatDuration(duration)}
        </span>
      </a>

      <div className="flex-1 flex flex-col justify-between">
        <div>
          <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-2 leading-snug">
            <a
              href={youtubeUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="hover:text-blue-600 dark:hover:text-purple-400 transition-colors"
            >
              {title || "Untitled Video"}
            </a>
          </h2>

          <p className="text-sm font-medium text-blue-600 dark:text-blue-400 mb-4">
            {channel_title || "Unknown Channel"}
          </p>

          <div className="grid grid-cols-2 lg:grid-cols-4 gap-2 mb-4 text-sm text-gray-600 dark:text-gray-400">
            <div className="flex items-center gap-1.5 p-2 bg-gray-50 dark:bg-slate-700/50 rounded-lg">
              <Eye className="w-4 h-4 text-orange-500" />
              <span>{formatCount(view_count)} Views</span>
            </div>
            <div className="flex items-center gap-1.5 p-2 bg-gray-50 dark:bg-slate-700/50 rounded-lg">
              <ThumbsUp className="w-4 h-4 text-blue-500" />
              <span>{formatCount(like_count)} Likes</span>
            </div>
            <div className="flex items-center gap-1.5 p-2 bg-gray-50 dark:bg-slate-700/50 rounded-lg">
              <Calendar className="w-4 h-4 text-green-500" />
              <span>{formatDate(published_at)}</span>
            </div>
            <div className="flex items-center gap-1.5 px-3 py-1.5 bg-gradient-to-r from-green-500/10 to-teal-500/10 text-green-700 dark:text-green-400 font-semibold rounded-lg border border-green-500/30">
              <TrendingUp className="w-4 h-4" />
              <span className="text-sm">
                {similarity_score ? (similarity_score * 100).toFixed(1) : "N/A"}% Match
              </span>
            </div>
          </div>

          {transcript_preview && (
            <p className="text-base text-gray-700 dark:text-gray-300 line-clamp-3 mb-4 italic border-l-4 border-blue-500/50 pl-3 flex items-start gap-2">
              <BookOpen className="w-4 h-4 text-blue-500 mt-1" />
              "{transcript_preview}"
            </p>
          )}
        </div>

        <a
          href={youtubeUrl}
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex items-center justify-center w-full md:w-auto px-6 py-2.5 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-xl font-semibold shadow-lg hover:shadow-xl hover:scale-[1.01] transition-all duration-200 mt-4 md:mt-0"
        >
          Watch Video
          <ExternalLink className="w-4 h-4 ml-2" />
        </a>
      </div>
    </motion.div>
  );
};

export default ResultCard;
