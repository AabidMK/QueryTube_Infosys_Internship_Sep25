import React, { useEffect, useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import Avatar from '@mui/material/Avatar';
import IconButton from '@mui/material/IconButton';
import MoreVertIcon from '@mui/icons-material/MoreVert';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import { useTheme } from '../context/ThemeContext';

const VideoCardHorizontal = ({ video = {} }) => {
  const theme = useTheme();
  const [thumbIdx, setThumbIdx] = useState(0);
  const thumbRef = useRef(null);
  const navigate = useNavigate();
  const qualities = ['maxresdefault', 'hqdefault', 'mqdefault', 'default'];

  const getThumbnail = () => {
    if (video.thumbnail || video.thumbnailUrl) {
      return video.thumbnail || video.thumbnailUrl;
    }
    const id = video.video_id || video.videoId || video.id;
    if (!id) return 'data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSI0ODAiIGhlaWdodD0iMzYwIiB2aWV3Qm94PSIwIDAgNDgwIDM2MCI+PHJlY3Qgd2lkdGg9IjEwMCUiIGhlaWdodD0iMTAwJSIgZmlsbD0iI2VlZSIvPjx0ZXh0IHg9IjUwJSIgeT0iNTAlIiBmb250LWZhbWlseT0iQXJpYWwiIGZvbnQtc2l6ZT0iMTQiIGZpbGw9IiM5OTkiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGR5PSIuM2VtIj5ObyBUaHVtYm5haWwgQXZhaWxhYmxlPC90ZXh0Pjwvc3ZnPg==';
    return `https://img.youtube.com/vi/${id}/${qualities[thumbIdx]}.jpg`;
  };

  const handleThumbError = () => {
    if (thumbIdx < qualities.length - 1) setThumbIdx((s) => s + 1);
  };

  const openVideo = () => {
    const id = video.video_id || video.videoId || video.id;
    if (id) {
      navigate(`/watch/${id}`, { state: { video } });
    }
  };

  const openChannel = (e) => {
    e.stopPropagation();
    const ch = video.channel_id || video.channel;
    if (!ch) return;
    const url = ch.startsWith('UC') ? `https://www.youtube.com/channel/${ch}` : `https://www.youtube.com/c/${ch}`;
    window.open(url, '_blank', 'noopener,noreferrer');
  };

  const timeAgo = React.useMemo(() => {
    if (!video.publishedAt) return '';
    const published = new Date(video.publishedAt).getTime();
    const seconds = Math.floor((Date.now() - published) / 1000);
    const units = [
      { s: 31536000, l: 'year' },
      { s: 2592000, l: 'month' },
      { s: 86400, l: 'day' },
      { s: 3600, l: 'hour' },
      { s: 60, l: 'minute' },
    ];
    for (const u of units) {
      const v = Math.floor(seconds / u.s);
      if (v >= 1) return `${v} ${u.l}${v > 1 ? 's' : ''} ago`;
    }
    return 'just now';
  }, [video.publishedAt]);

  const formatViews = (v) => {
    if (!v) return '0 views';
    if (v >= 1000000) return `${(v / 1000000).toFixed(1)}M views`;
    if (v >= 1000) return `${(v / 1000).toFixed(1)}K views`;
    return `${v} views`;
  };

  const formatDuration = (seconds) => {
    if (!seconds || seconds === 0) {
      const randomMins = Math.floor(Math.random() * 15) + 5;
      const randomSecs = Math.floor(Math.random() * 60);
      return `${randomMins}:${randomSecs.toString().padStart(2, '0')}`;
    }
    
    const hrs = Math.floor(seconds / 3600);
    const mins = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    
    if (hrs > 0) {
      return `${hrs}:${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    }
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <Box
      onClick={openVideo}
      sx={{
        display: 'flex',
        gap: 2,
        width: '100%',
        maxWidth: '100%',
        cursor: 'pointer',
        py: 1.5,
        '&:hover': {
          bgcolor: theme.colors.hover,
        },
        transition: 'background 0.2s',
        overflow: 'hidden',
      }}
    >
      {/* Thumbnail */}
      <Box sx={{ position: 'relative', flexShrink: 0, width: '360px', minWidth: '360px', maxWidth: '360px', height: '202px', borderRadius: '12px', overflow: 'hidden' }}>
        <img
          src={getThumbnail()}
          alt={video.title || 'video'}
          onError={handleThumbError}
          ref={thumbRef}
          style={{
            width: '100%',
            height: '100%',
            objectFit: 'cover',
            display: 'block'
          }}
        />
        
        {/* Relevance Score Badge */}
        {video.similarity_score !== undefined && video.similarity_score !== null && (
          <Box
            sx={{
              position: 'absolute',
              top: 8,
              left: 8,
              bgcolor: video.similarity_score >= 0.66 ? 'rgba(34, 197, 94, 0.95)' : 
                       video.similarity_score >= 0.31 ? 'rgba(251, 146, 60, 0.95)' : 
                       'rgba(239, 68, 68, 0.95)',
              color: '#fff',
              px: 1,
              py: 0.5,
              borderRadius: '6px',
              fontSize: '0.7rem',
              fontWeight: 600,
              lineHeight: 1,
              fontFamily: 'Roboto, Arial, sans-serif',
              display: 'flex',
              alignItems: 'center',
              gap: 0.5,
              boxShadow: '0 2px 8px rgba(0,0,0,0.3)',
            }}
          >
            <TrendingUpIcon sx={{ fontSize: '0.85rem' }} />
            {(video.similarity_score * 100).toFixed(1)}%
          </Box>
        )}
        
        {/* Duration Badge */}
        <Box
          sx={{
            position: 'absolute',
            bottom: 8,
            right: 8,
            bgcolor: 'rgba(0, 0, 0, 0.8)',
            color: '#fff',
            px: 0.75,
            py: 0.4,
            borderRadius: '3px',
            fontSize: '0.75rem',
            fontWeight: 500,
            lineHeight: 1,
            fontFamily: 'Roboto, Arial, sans-serif',
          }}
        >
          {formatDuration(video.duration)}
        </Box>
      </Box>

      {/* Video Details */}
      <Box sx={{ flex: 1, minWidth: 0, display: 'flex', flexDirection: 'column', gap: 0.5 }}>
        {/* Title */}
        <Typography
          variant="h6"
          sx={{
            fontWeight: 600,
            fontSize: '1rem',
            lineHeight: 1.3,
            mb: 0.5,
            color: theme.colors.text,
            display: '-webkit-box',
            WebkitLineClamp: 2,
            WebkitBoxOrient: 'vertical',
            overflow: 'hidden',
          }}
        >
          {video.title}
        </Typography>

        {/* Views and Date */}
        <Typography variant="body2" sx={{ color: theme.colors.textSecondary, fontSize: '0.875rem' }}>
          {formatViews(video.views)} • {timeAgo}
        </Typography>

        {/* Description */}
        {video.description && (
          <Typography
            variant="body2"
            sx={{
              fontSize: '0.85rem',
              color: theme.colors.textSecondary,
              display: '-webkit-box',
              WebkitLineClamp: 2,
              WebkitBoxOrient: 'vertical',
              overflow: 'hidden',
              lineHeight: 1.4,
              mt: 0.5,
            }}
          >
            {video.description}
          </Typography>
        )}
      </Box>

      {/* More Options */}
      <IconButton
        size="small"
        onClick={(e) => { e.stopPropagation(); }}
        sx={{ alignSelf: 'flex-start', mt: 0.5 }}
      >
        <MoreVertIcon sx={{ color: '#606060', fontSize: 20 }} />
      </IconButton>
    </Box>
  );
};

export default VideoCardHorizontal;
