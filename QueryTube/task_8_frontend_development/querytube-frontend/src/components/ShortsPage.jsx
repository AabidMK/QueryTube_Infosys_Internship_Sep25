import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Box, 
  IconButton, 
  Typography, 
  Avatar, 
  CircularProgress,
  Drawer,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  useTheme as useMuiTheme,
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
import MoreVertIcon from '@mui/icons-material/MoreVert';
import VolumeUpIcon from '@mui/icons-material/VolumeUp';
import VolumeOffIcon from '@mui/icons-material/VolumeOff';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import PauseIcon from '@mui/icons-material/Pause';
import Navbar from './Navbar';
import { getInitialVideos } from '../services/api';
import ShortsIconPng from '../assets/QueryTube_Short.png';
import { useTheme } from '../context/ThemeContext';

const DRAWER_WIDTH = 240;

const ShortsPage = () => {
  const navigate = useNavigate();
  const theme = useTheme();
  const muiTheme = useMuiTheme();
  const isMobile = useMediaQuery(muiTheme.breakpoints.down('sm'));
  const [sidebarOpen, setSidebarOpen] = useState(true);

  const sidebarItems = [
    { text: 'Home', icon: <HomeIcon />, path: '/' },
    { text: 'Shorts', icon: <Box component="img" src={ShortsIconPng} alt="Shorts" sx={{ width: 22, height: 22 }} />, path: '/shorts' },
    { text: 'Trending', icon: <WhatshotIcon />, path: '/trending' },
    { text: 'Subscriptions', icon: <SubscriptionsIcon />, path: '/subscriptions' },
    { text: 'Library', icon: <VideoLibraryIcon />, path: '/library' },
    { text: 'History', icon: <HistoryIcon />, path: '/history' },
  ];
  const [shorts, setShorts] = useState([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [loading, setLoading] = useState(true);
  const [hasMore, setHasMore] = useState(true);
  const [page, setPage] = useState(0);
  const [muted, setMuted] = useState(false);
  const [playing, setPlaying] = useState(true);
  const containerRef = useRef(null);
  const isLoadingMore = useRef(false);

  const PAGE_SIZE = 10;

  useEffect(() => {
    loadInitialShorts();
  }, []);

  const loadInitialShorts = async () => {
    try {
      setLoading(true);
      const { videos: newVideos, hasMore: moreAvailable } = await getInitialVideos(0, PAGE_SIZE);
      // Filter videos with is_short = true
      const shortVideos = newVideos.filter(video => {
        // If is_short field exists, use it
        if (video.is_short !== undefined) {
          return video.is_short === true;
        }
        // Fallback: if duration exists, check if < 120 seconds
        if (video.duration && video.duration > 0) {
          return video.duration < 120;
        }
        // If no data, don't include in shorts
        return false;
      });
      setShorts(shortVideos);
      setHasMore(moreAvailable);
      setPage(0);
    } catch (err) {
      console.error('Shorts loading error:', err);
    } finally {
      setLoading(false);
    }
  };

  const loadMoreShorts = async () => {
    if (!hasMore || isLoadingMore.current) return;
    
    isLoadingMore.current = true;
    try {
      const offset = (page + 1) * PAGE_SIZE;
      const { videos: newVideos, hasMore: moreAvailable } = await getInitialVideos(offset, PAGE_SIZE);
      const shortVideos = newVideos.filter(video => {
        if (video.is_short !== undefined) return video.is_short === true;
        if (video.duration && video.duration > 0) return video.duration < 120;
        return false;
      });
      
      // Remove duplicates
      const existingIds = new Set(shorts.map(v => v.video_id));
      const uniqueShorts = shortVideos.filter(v => !existingIds.has(v.video_id));
      
      if (uniqueShorts.length > 0) {
        setShorts(prev => [...prev, ...uniqueShorts]);
      }
      setHasMore(moreAvailable);
      setPage(prev => prev + 1);
    } catch (err) {
      console.error('Load more shorts error:', err);
    } finally {
      isLoadingMore.current = false;
    }
  };

  const handleScroll = (e) => {
    const container = e.target;
    const scrollTop = container.scrollTop;
    const scrollHeight = container.scrollHeight;
    const clientHeight = container.clientHeight;
    
    // Calculate which video is currently in view
    const videoHeight = clientHeight;
    const newIndex = Math.round(scrollTop / videoHeight);
    
    if (newIndex !== currentIndex && newIndex < shorts.length) {
      setCurrentIndex(newIndex);
    }
    
    // Load more when near the end
    if (scrollHeight - scrollTop - clientHeight < 500 && hasMore) {
      loadMoreShorts();
    }
  };

  const formatViews = (v) => {
    if (!v) return '0 views';
    if (v >= 1000000) return `${(v / 1000000).toFixed(1)}M views`;
    if (v >= 1000) return `${(v / 1000).toFixed(1)}K views`;
    return `${v} views`;
  };

  const formatNumber = (num) => {
    if (!num) return '0';
    if (num >= 1000000) return `${(num / 1000000).toFixed(1)}M`;
    if (num >= 1000) return `${(num / 1000).toFixed(1)}K`;
    return num.toString();
  };

  const openVideo = (videoId) => {
    if (videoId) {
      window.open(`https://www.youtube.com/watch?v=${videoId}`, '_blank', 'noopener,noreferrer');
    }
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="100vh" bgcolor="#000">
        <CircularProgress sx={{ color: '#fff' }} />
      </Box>
    );
  }

  if (shorts.length === 0) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="100vh" bgcolor="#000">
        <Typography variant="h6" color="#fff">No Shorts available (videos under 2 minutes)</Typography>
      </Box>
    );
  }

  const currentShort = shorts[currentIndex];

  const handleSidebarItemClick = (path) => {
    navigate(path);
  };

  const handleSearch = (query) => {
    // Navigate to home with search query
    navigate('/', { state: { searchQuery: query } });
  };

  return (
    <Box sx={{ display: 'flex', minHeight: '100vh', bgcolor: '#000', transition: 'background-color 0.3s' }}>
      <Navbar onSearch={handleSearch} sidebarOpen={sidebarOpen} setSidebarOpen={setSidebarOpen} />

      {!isMobile && (
        <>
          <Drawer
            variant="persistent"
            open={true}
            sx={{
              width: sidebarOpen ? DRAWER_WIDTH : 72,
              flexShrink: 0,
              transition: 'width 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
              '& .MuiDrawer-paper': {
                width: sidebarOpen ? DRAWER_WIDTH : 72,
                boxSizing: 'border-box',
                top: '64px',
                height: 'calc(100% - 64px)',
                bgcolor: theme.colors.surface,
                borderRight: `1.5px solid ${theme.colors.border}`,
                boxShadow: 'none',
                transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                p: 0,
                overflowY: 'auto',
                overflowX: 'hidden',
              },
            }}
          >
            <List sx={{ p: 0, pt: 1 }}>
              {sidebarItems.map((item, idx) => (
                <ListItem
                  key={item.text}
                  onClick={() => handleSidebarItemClick(item.path)}
                  sx={{
                    py: 1.2,
                    px: sidebarOpen ? 2.5 : 0,
                    borderRadius: 2,
                    mx: sidebarOpen ? 1 : 0.5,
                    my: 0.5,
                    color: item.path === '/shorts' ? theme.colors.primary : theme.colors.text,
                    bgcolor: item.path === '/shorts' ? theme.colors.primaryHover : 'transparent',
                    fontWeight: item.path === '/shorts' ? 700 : 500,
                    display: 'flex',
                    justifyContent: sidebarOpen ? 'flex-start' : 'center',
                    alignItems: 'center',
                    '&:hover': {
                      bgcolor: theme.colors.hover,
                      cursor: 'pointer',
                    },
                    transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                    minHeight: 44,
                  }}
                  component="button"
                >
                  <ListItemIcon sx={{ 
                    color: item.path === '/shorts' ? theme.colors.primary : theme.colors.textSecondary, 
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
                        fontWeight: item.path === '/shorts' ? 700 : 500, 
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
        </>
      )}

      <Box
        ref={containerRef}
        onScroll={handleScroll}
        component="main"
        sx={{
          flexGrow: 1,
          width: '100%',
          height: 'calc(100vh - 64px)',
          overflowY: 'scroll',
          scrollSnapType: 'y mandatory',
          bgcolor: '#000',
          position: 'relative',
          mt: '64px',
          ml: !isMobile ? (sidebarOpen ? `${DRAWER_WIDTH}px` : '72px') : 0,
          transition: 'margin 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
          '&::-webkit-scrollbar': { display: 'none' },
          scrollbarWidth: 'none',
        }}
      >
      {shorts.map((short, index) => (
        <Box
          key={`${short.video_id}-${index}`}
          sx={{
            width: '100%',
            height: 'calc(100vh - 64px)',
            scrollSnapAlign: 'start',
            position: 'relative',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            bgcolor: '#000',
          }}
        >
          {/* Video Thumbnail/Poster */}
          <Box
            component="img"
            src={short.thumbnail_url || `https://img.youtube.com/vi/${short.video_id}/maxresdefault.jpg`}
            alt={short.title}
            onClick={() => openVideo(short.video_id)}
            sx={{
              maxWidth: '100%',
              maxHeight: '100%',
              objectFit: 'contain',
              cursor: 'pointer',
            }}
          />

          {/* Play/Pause Overlay */}
          <IconButton
            onClick={() => setPlaying(!playing)}
            sx={{
              position: 'absolute',
              top: '50%',
              left: '50%',
              transform: 'translate(-50%, -50%)',
              bgcolor: 'rgba(0, 0, 0, 0.5)',
              color: '#fff',
              '&:hover': { bgcolor: 'rgba(0, 0, 0, 0.7)' },
            }}
          >
            {playing ? <PauseIcon fontSize="large" /> : <PlayArrowIcon fontSize="large" />}
          </IconButton>

          {/* Right Side Action Buttons */}
          <Box
            sx={{
              position: 'absolute',
              right: 12,
              bottom: 80,
              display: 'flex',
              flexDirection: 'column',
              gap: 3,
              alignItems: 'center',
            }}
          >
            {/* Like */}
            <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
              <IconButton sx={{ color: '#fff', bgcolor: 'rgba(0, 0, 0, 0.4)' }}>
                <ThumbUpOutlinedIcon />
              </IconButton>
              <Typography variant="caption" sx={{ color: '#fff', mt: 0.5 }}>
                {formatNumber(short.likes)}
              </Typography>
            </Box>

            {/* Dislike */}
            <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
              <IconButton sx={{ color: '#fff', bgcolor: 'rgba(0, 0, 0, 0.4)' }}>
                <ThumbDownOutlinedIcon />
              </IconButton>
              <Typography variant="caption" sx={{ color: '#fff', mt: 0.5 }}>
                Dislike
              </Typography>
            </Box>

            {/* Share */}
            <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
              <IconButton sx={{ color: '#fff', bgcolor: 'rgba(0, 0, 0, 0.4)' }}>
                <ShareOutlinedIcon />
              </IconButton>
              <Typography variant="caption" sx={{ color: '#fff', mt: 0.5 }}>
                Share
              </Typography>
            </Box>

            {/* More */}
            <IconButton sx={{ color: '#fff', bgcolor: 'rgba(0, 0, 0, 0.4)' }}>
              <MoreVertIcon />
            </IconButton>

            {/* Channel Avatar */}
            <Avatar
              sx={{
                width: 40,
                height: 40,
                border: '2px solid #fff',
                cursor: 'pointer',
              }}
              src={`https://ui-avatars.com/api/?name=${encodeURIComponent(short.channel || '')}&background=random`}
            />
          </Box>

          {/* Bottom Info */}
          <Box
            sx={{
              position: 'absolute',
              bottom: 0,
              left: 0,
              right: 60,
              p: 2,
              background: 'linear-gradient(transparent, rgba(0, 0, 0, 0.8))',
              color: '#fff',
            }}
          >
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, mb: 1 }}>
              <Avatar
                sx={{ width: 32, height: 32 }}
                src={`https://ui-avatars.com/api/?name=${encodeURIComponent(short.channel || '')}&background=random`}
              />
              <Typography variant="body2" fontWeight={600}>
                {short.channel}
              </Typography>
            </Box>
            <Typography variant="body2" sx={{ mb: 0.5 }}>
              {short.title}
            </Typography>
            <Typography variant="caption" sx={{ color: '#aaa' }}>
              {formatViews(short.views)}
            </Typography>
          </Box>

          {/* Top Right Controls */}
          <Box
            sx={{
              position: 'absolute',
              top: 16,
              right: 16,
              display: 'flex',
              gap: 1,
            }}
          >
            <IconButton
              onClick={() => setMuted(!muted)}
              sx={{ color: '#fff', bgcolor: 'rgba(0, 0, 0, 0.5)' }}
            >
              {muted ? <VolumeOffIcon /> : <VolumeUpIcon />}
            </IconButton>
          </Box>
        </Box>
      ))}

      {/* Loading indicator at bottom */}
        {hasMore && (
          <Box display="flex" justifyContent="center" py={2} bgcolor="#000">
            <CircularProgress size={24} sx={{ color: '#fff' }} />
          </Box>
        )}
      </Box>
    </Box>
  );
};

export default ShortsPage;
