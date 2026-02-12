import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, useLocation } from 'react-router-dom';
import {
  Box,
  Typography,
  Avatar,
  Button,
  Divider,
  IconButton,
  Chip,
  Drawer,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  useTheme,
  useMediaQuery,
} from '@mui/material';
import HomeIcon from '@mui/icons-material/Home';
import WhatshotIcon from '@mui/icons-material/Whatshot';
import SubscriptionsIcon from '@mui/icons-material/Subscriptions';
import VideoLibraryIcon from '@mui/icons-material/VideoLibrary';
import HistoryIcon from '@mui/icons-material/History';
import ThumbUpOutlinedIcon from '@mui/icons-material/ThumbUpOutlined';
import ThumbDownOutlinedIcon from '@mui/icons-material/ThumbDownOutlined';
import ShareOutlinedIcon from '@mui/icons-material/ShareOutlined';
import DownloadOutlinedIcon from '@mui/icons-material/DownloadOutlined';
import MoreHorizIcon from '@mui/icons-material/MoreHoriz';
import Navbar from './Navbar';
import { getInitialVideos } from '../services/api';
import ShortsIconPng from '../assets/QueryTube_Short.png';

const DRAWER_WIDTH = 240;

const VideoPlayer = () => {
  const { videoId } = useParams();
  const navigate = useNavigate();
  const location = useLocation();
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const videoData = location.state?.video;

  const [relatedVideos, setRelatedVideos] = useState([]);
  const [showFullDescription, setShowFullDescription] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const sidebarItems = [
    { text: 'Home', icon: <HomeIcon />, path: '/' },
    { text: 'Shorts', icon: <Box component="img" src={ShortsIconPng} alt="Shorts" sx={{ width: 22, height: 22 }} />, path: '/shorts' },
    { text: 'Trending', icon: <WhatshotIcon />, path: '/trending' },
    { text: 'Subscriptions', icon: <SubscriptionsIcon />, path: '/subscriptions' },
    { text: 'Library', icon: <VideoLibraryIcon />, path: '/library' },
    { text: 'History', icon: <HistoryIcon />, path: '/history' },
  ];

  useEffect(() => {
    loadRelatedVideos();
  }, []);

  const loadRelatedVideos = async () => {
    try {
      const { videos } = await getInitialVideos(0, 20);
      setRelatedVideos(videos.filter(v => v.video_id !== videoId));
    } catch (err) {
      console.error('Error loading related videos:', err);
    }
  };

  const formatViews = (views) => {
    if (!views) return '0 views';
    if (views >= 1000000) return `${(views / 1000000).toFixed(1)}M views`;
    if (views >= 1000) return `${(views / 1000).toFixed(1)}K views`;
    return `${views} views`;
  };

  const formatNumber = (num) => {
    if (!num) return '0';
    if (num >= 1000000) return `${(num / 1000000).toFixed(1)}M`;
    if (num >= 1000) return `${(num / 1000).toFixed(1)}K`;
    return num.toString();
  };

  const timeAgo = (publishedAt) => {
    if (!publishedAt) return '';
    const published = new Date(publishedAt).getTime();
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
  };

  const handleVideoClick = (video) => {
    navigate(`/watch/${video.video_id}`, { state: { video } });
    window.scrollTo(0, 0);
  };

  const handleSearch = (query) => {
    navigate('/', { state: { searchQuery: query } });
  };

  const handleSidebarItemClick = (path) => {
    navigate(path);
  };

  return (
    <Box sx={{ display: 'flex', bgcolor: '#f9f9f9', minHeight: '100vh' }}>
      <Navbar onSearch={handleSearch} sidebarOpen={sidebarOpen} setSidebarOpen={setSidebarOpen} />

      {/* Backdrop overlay when sidebar is open */}
      {sidebarOpen && !isMobile && (
        <Box
          onClick={() => setSidebarOpen(false)}
          sx={{
            position: 'fixed',
            top: '64px',
            left: 0,
            right: 0,
            bottom: 0,
            bgcolor: 'rgba(0, 0, 0, 0.5)',
            zIndex: 1200,
          }}
        />
      )}


      {/* Full sidebar (overlay when open) */}
      {!isMobile && (
        <Drawer
          variant="temporary"
          open={sidebarOpen}
          onClose={() => setSidebarOpen(false)}
          sx={{
            width: DRAWER_WIDTH,
            flexShrink: 0,
            zIndex: 1300,
            '& .MuiDrawer-paper': {
              width: DRAWER_WIDTH,
              boxSizing: 'border-box',
              top: '64px',
              height: 'calc(100% - 64px)',
              bgcolor: '#fff',
              borderRight: 'none',
              boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
              p: 0,
              overflowY: 'auto',
              overflowX: 'hidden',
            },
          }}
        >
          <List sx={{ p: 0, pt: 1 }}>
            {sidebarItems.map((item) => (
              <ListItem
                key={item.text}
                onClick={() => handleSidebarItemClick(item.path)}
                sx={{
                  py: 1.2,
                  px: sidebarOpen ? 2.5 : 0,
                  borderRadius: 2,
                  mx: sidebarOpen ? 1 : 0.5,
                  my: 0.5,
                  color: location.pathname === item.path ? '#ff0000' : '#222',
                  bgcolor: location.pathname === item.path ? 'rgba(255,0,0,0.08)' : 'transparent',
                  fontWeight: location.pathname === item.path ? 700 : 500,
                  display: 'flex',
                  justifyContent: sidebarOpen ? 'flex-start' : 'center',
                  alignItems: 'center',
                  '&:hover': {
                    bgcolor: 'rgba(0,0,0,0.04)',
                    cursor: 'pointer',
                  },
                  transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                  minHeight: 44,
                }}
                component="button"
              >
                <ListItemIcon sx={{ 
                  color: location.pathname === item.path ? '#ff0000' : '#606060', 
                  minWidth: 36,
                  justifyContent: sidebarOpen ? 'flex-start' : 'center',
                  transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                }}>
                  {item.icon}
                </ListItemIcon>
                {sidebarOpen && (
                  <ListItemText 
                    primary={item.text} 
                    primaryTypographyProps={{ 
                      fontWeight: location.pathname === item.path ? 700 : 500, 
                      fontSize: 15,
                      sx: {
                        opacity: sidebarOpen ? 1 : 0,
                        transition: 'opacity 0.2s cubic-bezier(0.4, 0, 0.2, 1)',
                      }
                    }} 
                  />
                )}
              </ListItem>
            ))}
          </List>
        </Drawer>
      )}

      <Box sx={{ 
        display: 'flex', 
        pt: '88px', 
        px: { xs: 2, md: 3 }, 
        gap: 3, 
        maxWidth: '1920px', 
        mx: 'auto',
        ml: 0,
        width: '100%',
      }}>
        {/* Main Video Section */}
        <Box sx={{ flex: 1, maxWidth: '1280px', pr: 0 }}>
          {/* Video Player */}
          <Box
            sx={{
              position: 'relative',
              width: '100%',
              paddingTop: '56.25%',
              bgcolor: '#000',
              borderRadius: '12px',
              overflow: 'hidden',
              mb: 2,
            }}
          >
            <iframe
              style={{
                position: 'absolute',
                top: 0,
                left: 0,
                width: '100%',
                height: '100%',
                border: 'none',
              }}
              src={`https://www.youtube.com/embed/${videoId}?autoplay=1`}
              title="YouTube video player"
              allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
              allowFullScreen
            />
          </Box>

          {/* Video Title */}
          <Typography variant="h5" sx={{ fontWeight: 600, mb: 1.5, mt: 1.5, color: '#0f0f0f', fontSize: '1.25rem' }}>
            {videoData?.title || 'Video Title'}
          </Typography>

          {/* Video Info Bar */}
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 1.5, flexWrap: 'wrap', gap: 2 }}>
            {/* Channel Info */}
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
              <Avatar
                sx={{ width: 40, height: 40 }}
                src={videoData?.channelAvatar || `https://ui-avatars.com/api/?name=${encodeURIComponent(videoData?.channel || 'Channel')}&background=random`}
              />
              <Box>
                <Typography variant="body1" sx={{ fontWeight: 600, color: '#0f0f0f' }}>
                  {videoData?.channel || 'Channel Name'}
                </Typography>
                <Typography variant="body2" sx={{ color: '#606060', fontSize: '0.85rem' }}>
                  {formatViews(videoData?.views)} • {timeAgo(videoData?.publishedAt)}
                </Typography>
              </Box>
              <Button
                variant="contained"
                sx={{
                  ml: 2,
                  bgcolor: '#0f0f0f',
                  color: '#fff',
                  textTransform: 'none',
                  borderRadius: '18px',
                  px: 2,
                  '&:hover': { bgcolor: '#272727' },
                }}
              >
                Subscribe
              </Button>
            </Box>

            {/* Action Buttons */}
            <Box sx={{ display: 'flex', gap: 1 }}>
              <Button
                startIcon={<ThumbUpOutlinedIcon />}
                sx={{
                  bgcolor: '#f2f2f2',
                  color: '#0f0f0f',
                  textTransform: 'none',
                  borderRadius: '18px',
                  px: 2,
                  '&:hover': { bgcolor: '#e5e5e5' },
                }}
              >
                {formatNumber(videoData?.likes)}
              </Button>
              <Button
                startIcon={<ThumbDownOutlinedIcon />}
                sx={{
                  bgcolor: '#f2f2f2',
                  color: '#0f0f0f',
                  textTransform: 'none',
                  borderRadius: '18px',
                  px: 2,
                  '&:hover': { bgcolor: '#e5e5e5' },
                }}
              >
                Dislike
              </Button>
              <Button
                startIcon={<ShareOutlinedIcon />}
                sx={{
                  bgcolor: '#f2f2f2',
                  color: '#0f0f0f',
                  textTransform: 'none',
                  borderRadius: '18px',
                  px: 2,
                  '&:hover': { bgcolor: '#e5e5e5' },
                }}
              >
                Share
              </Button>
              <Button
                startIcon={<DownloadOutlinedIcon />}
                sx={{
                  bgcolor: '#f2f2f2',
                  color: '#0f0f0f',
                  textTransform: 'none',
                  borderRadius: '18px',
                  px: 2,
                  '&:hover': { bgcolor: '#e5e5e5' },
                }}
              >
                Download
              </Button>
              <IconButton
                sx={{
                  bgcolor: '#f2f2f2',
                  '&:hover': { bgcolor: '#e5e5e5' },
                }}
              >
                <MoreHorizIcon />
              </IconButton>
            </Box>
          </Box>

          {/* Description Box */}
          <Box
            sx={{
              bgcolor: '#f2f2f2',
              borderRadius: '12px',
              p: 2,
              cursor: 'pointer',
              '&:hover': { bgcolor: '#e5e5e5' },
            }}
            onClick={() => setShowFullDescription(!showFullDescription)}
          >
            <Typography
              variant="body2"
              sx={{
                color: '#0f0f0f',
                whiteSpace: showFullDescription ? 'pre-wrap' : 'nowrap',
                overflow: 'hidden',
                textOverflow: 'ellipsis',
              }}
            >
              {videoData?.description || 'No description available'}
            </Typography>
            {!showFullDescription && (
              <Typography variant="body2" sx={{ color: '#0f0f0f', fontWeight: 600, mt: 1 }}>
                ...more
              </Typography>
            )}
          </Box>

          <Divider sx={{ my: 3 }} />

          {/* Comments Section Placeholder */}
          <Typography variant="h6" sx={{ fontWeight: 600, mb: 2 }}>
            {formatNumber(videoData?.comment_count || 0)} Comments
          </Typography>
        </Box>

        {/* Related Videos Sidebar */}
        <Box sx={{ width: '402px', flexShrink: 0, pl: 0 }}>
          {/* Filter Chips */}
          <Box sx={{ display: 'flex', gap: 1, mb: 2, overflowX: 'auto', pb: 1, '&::-webkit-scrollbar': { display: 'none' } }}>
            <Chip label="All" sx={{ bgcolor: '#0f0f0f', color: '#fff', fontWeight: 500 }} />
            <Chip label="From Channel" sx={{ bgcolor: '#f2f2f2', '&:hover': { bgcolor: '#e5e5e5' } }} />
            <Chip label="Related" sx={{ bgcolor: '#f2f2f2', '&:hover': { bgcolor: '#e5e5e5' } }} />
          </Box>

          {/* Related Videos List */}
          {relatedVideos.map((video, index) => (
            <Box
              key={`${video.video_id}-${index}`}
              onClick={() => handleVideoClick(video)}
              sx={{
                display: 'flex',
                gap: 1.5,
                mb: 1.5,
                cursor: 'pointer',
                '&:hover': {
                  bgcolor: 'rgba(0,0,0,0.02)',
                },
                p: 0.5,
                borderRadius: '8px',
              }}
            >
              {/* Thumbnail */}
              <Box
                component="img"
                src={video.thumbnail_url || `https://img.youtube.com/vi/${video.video_id}/mqdefault.jpg`}
                alt={video.title}
                sx={{
                  width: '168px',
                  height: '94px',
                  borderRadius: '8px',
                  objectFit: 'cover',
                  flexShrink: 0,
                }}
              />

              {/* Video Info */}
              <Box sx={{ flex: 1, minWidth: 0 }}>
                <Typography
                  variant="body2"
                  sx={{
                    fontWeight: 600,
                    color: '#0f0f0f',
                    display: '-webkit-box',
                    WebkitLineClamp: 2,
                    WebkitBoxOrient: 'vertical',
                    overflow: 'hidden',
                    fontSize: '0.9rem',
                    lineHeight: 1.3,
                    mb: 0.5,
                  }}
                >
                  {video.title}
                </Typography>
                <Typography variant="caption" sx={{ color: '#606060', display: 'block' }}>
                  {video.channel}
                </Typography>
                <Typography variant="caption" sx={{ color: '#606060', display: 'block' }}>
                  {formatViews(video.views)} • {timeAgo(video.publishedAt)}
                </Typography>
              </Box>
            </Box>
          ))}
        </Box>
      </Box>
    </Box>
  );
};

export default VideoPlayer;
