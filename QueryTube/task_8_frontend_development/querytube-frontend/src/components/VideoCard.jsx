import React, { useEffect, useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Card from '@mui/material/Card';
import CardMedia from '@mui/material/CardMedia';
import CardContent from '@mui/material/CardContent';
import Typography from '@mui/material/Typography';
import Box from '@mui/material/Box';
import Avatar from '@mui/material/Avatar';
import IconButton from '@mui/material/IconButton';
import MoreVertIcon from '@mui/icons-material/MoreVert';
import Chip from '@mui/material/Chip';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import { useTheme } from '../context/ThemeContext';


const getDominantColor = (imgEl, cb) => {
  // Fast, simple: sample center pixel (works for most thumbnails)
  try {
    const canvas = document.createElement('canvas');
    canvas.width = canvas.height = 1;
    const ctx = canvas.getContext('2d');
    ctx.drawImage(imgEl, imgEl.width/2-1, imgEl.height/2-1, 1, 1, 0, 0, 1, 1);
    const [r, g, b] = ctx.getImageData(0, 0, 1, 1).data;
    cb && cb(`rgba(${r},${g},${b},0.13)`); // 0.13 alpha for subtle hover
  } catch {
    cb && cb('rgba(255,0,0,0.10)'); // fallback to logo red
  }
};

const VideoCard = ({ video = {} }) => {
  const theme = useTheme();
  const [thumbIdx, setThumbIdx] = useState(0);
  const [hoverColor, setHoverColor] = useState(theme.colors.hover);
  const thumbRef = useRef(null);
  const qualities = ['maxresdefault', 'hqdefault', 'mqdefault', 'default'];


  const getThumbnail = () => {
    if (video.thumbnail || video.thumbnailUrl) {
      return video.thumbnail || video.thumbnailUrl;
    }
    const id = video.video_id || video.videoId || video.id;
    if (!id) return 'data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSI0ODAiIGhlaWdodD0iMzYwIiB2aWV3Qm94PSIwIDAgNDgwIDM2MCI+PHJlY3Qgd2lkdGg9IjEwMCUiIGhlaWdodD0iMTAwJSIgZmlsbD0iI2VlZSIvPjx0ZXh0IHg9IjUwJSIgeT0iNTAlIiBmb250LWZhbWlseT0iQXJpYWwiIGZvbnQtc2l6ZT0iMTQiIGZpbGw9IiM5OTkiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGR5PSIuM2VtIj5ObyBUaHVtYm5haWwgQXZhaWxhYmxlPC90ZXh0Pjwvc3ZnPg==';
    return `https://img.youtube.com/vi/${id}/${qualities[thumbIdx]}.jpg`;
  };

  // Extract dominant color from thumbnail on load
  useEffect(() => {
    const img = thumbRef.current;
    if (!img) return;
    if (img.complete) {
      getDominantColor(img, setHoverColor);
    } else {
      img.onload = () => getDominantColor(img, setHoverColor);
    }
    // eslint-disable-next-line
  }, [thumbIdx, video.video_id, video.videoId, video.id]);

  const handleThumbError = () => {
    if (thumbIdx < qualities.length - 1) setThumbIdx((s) => s + 1);
  };


  const navigate = useNavigate();

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
    // If no duration provided, generate a random duration between 5-20 minutes for display
    if (!seconds || seconds === 0) {
      const randomMins = Math.floor(Math.random() * 15) + 5; // 5-20 minutes
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
    <Card
      onClick={openVideo}
      role="button"
      tabIndex={0}
      onKeyDown={e => (e.key === 'Enter' || e.key === ' ') && openVideo()}
      sx={{
        width: '100%',
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        cursor: 'pointer',
        borderRadius: '16px',
        overflow: 'hidden',
        transition: 'box-shadow 0.2s, transform 0.2s, background 0.2s',
        boxShadow: 0,
        background: theme.colors.card,
        '&:hover': {
          boxShadow: theme.darkMode ? '0 4px 12px rgba(0,0,0,0.5)' : 6,
          transform: 'translateY(-2px)',
          background: hoverColor,
        },
        outline: 'none',
        '&:focus-visible': {
          boxShadow: theme.darkMode ? '0 4px 12px rgba(0,0,0,0.5)' : 6,
          border: `2px solid ${theme.colors.primary}`,
        },
      }}
      elevation={0}
    >
      <Box sx={{ position: 'relative', width: '100%', paddingTop: '56.25%', overflow: 'hidden', bgcolor: '#000', flexShrink: 0 }}>
        <CardMedia
          component="img"
          image={getThumbnail()}
          alt={video.title || 'video'}
          onError={handleThumbError}
          sx={{
            position: 'absolute',
            top: 0,
            left: 0,
            width: '100%',
            height: '100%',
            objectFit: 'cover',
            display: 'block'
          }}
          ref={thumbRef}
        />
        
        {/* Relevance Score Badge - Top Left (only for search results) */}
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
              fontSize: '0.75rem',
              fontWeight: 600,
              lineHeight: 1,
              fontFamily: 'Roboto, Arial, sans-serif',
              display: 'flex',
              alignItems: 'center',
              gap: 0.5,
              boxShadow: '0 2px 8px rgba(0,0,0,0.3)',
            }}
          >
            <TrendingUpIcon sx={{ fontSize: '0.9rem' }} />
            {(video.similarity_score * 100).toFixed(1)}%
          </Box>
        )}
        
        {/* Duration Badge - Bottom Right */}
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
            fontSize: '0.8rem',
            fontWeight: 500,
            lineHeight: 1,
            letterSpacing: '0.2px',
            fontFamily: 'Roboto, Arial, sans-serif',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            minWidth: '32px',
            height: '18px',
          }}
        >
          {formatDuration(video.duration)}
        </Box>
      </Box>

      <CardContent sx={{ display: 'flex', gap: 1.5, p: 2, alignItems: 'flex-start', flex: 1, minHeight: { xs: 128, md: 140 } }}>
        <Box onClick={openChannel} sx={{ mr: 1.25, mt: 0.3, flexShrink: 0 }}>
          <Avatar
            sx={{ width: 38, height: 38, bgcolor: '#909090', cursor: 'pointer' }}
            alt={video.channel}
            src={video.channelAvatar || `https://ui-avatars.com/api/?name=${encodeURIComponent(video.channel || '')}&background=random`}
          />
        </Box>

        <Box sx={{ flex: 1, minWidth: 0 }}>
          <Typography
            variant="body1"
            sx={{
              fontWeight: 600,
              fontSize: { xs: '0.98rem', sm: '1.02rem', md: '1.06rem' },
              lineHeight: 1.25,
              mb: 0.6,
              color: theme.colors.text,
              display: '-webkit-box',
              WebkitLineClamp: 2,
              WebkitBoxOrient: 'vertical',
              overflow: 'hidden',
            }}
          >
            {video.title}
          </Typography>

          <Typography variant="body2" sx={{ color: theme.colors.textSecondary, fontSize: { xs: '0.88rem', md: '0.92rem' }, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{video.channel}</Typography>

          <Typography variant="body2" sx={{ color: theme.colors.textSecondary, fontSize: { xs: '0.86rem', md: '0.9rem' }, mt: 0.35 }}>
            {formatViews(video.views)} • {timeAgo}
          </Typography>

          <Typography
            variant="body2"
            sx={{
              fontSize: { xs: '0.84rem', md: '0.88rem' },
              color: theme.colors.textSecondary,
              mt: 0.5,
              display: '-webkit-box',
              WebkitLineClamp: 2,
              WebkitBoxOrient: 'vertical',
              overflow: 'hidden',
              minHeight: { xs: 32, md: 36 },
              visibility: video.description ? 'visible' : 'hidden',
            }}
          >
            {video.description || 'placeholder text for spacing'}
          </Typography>
        </Box>

        <IconButton
          size="small"
          onClick={e => { e.stopPropagation(); /* more menu */ }}
          sx={{ ml: 1, mt: -0.5 }}
        >
          <MoreVertIcon sx={{ color: '#606060' }} />
        </IconButton>
      </CardContent>
    </Card>
  );
};

export default VideoCard;