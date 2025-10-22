import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import {
  Box,
  CircularProgress,
  Alert,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Drawer,
  useTheme as useMuiTheme,
  useMediaQuery,
  Typography,
  Chip,
} from '@mui/material';
import HomeIcon from '@mui/icons-material/Home';
import WhatshotIcon from '@mui/icons-material/Whatshot';
import SubscriptionsIcon from '@mui/icons-material/Subscriptions';
import VideoLibraryIcon from '@mui/icons-material/VideoLibrary';
import HistoryIcon from '@mui/icons-material/History';
import Navbar from './components/Navbar';
import VideoCard from './components/VideoCard';
import VideoCardHorizontal from './components/VideoCardHorizontal';
import { searchVideos, getInitialVideos } from './services/api';
import SearchBar from './components/SearchBar';
import ShortsIconPng from './assets/QueryTube_Short.png';
import { useTheme } from './context/ThemeContext';

const DRAWER_WIDTH = 240;

const AppContent = () => {
  const [videos, setVideos] = useState([]);
  const [allVideos, setAllVideos] = useState([]); // Store all search results
  const [loading, setLoading] = useState(true);
  const [loadingMore, setLoadingMore] = useState(false);
  const [error, setError] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [hasMore, setHasMore] = useState(true);
  const [page, setPage] = useState(0);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [activeFilter, setActiveFilter] = useState('all'); // 'all', 'videos', 'shorts'
  
  const navigate = useNavigate();
  const location = useLocation();
  const theme = useTheme();
  const muiTheme = useMuiTheme();
  const isMobile = useMediaQuery(muiTheme.breakpoints.down('md'));

  const sidebarItems = [
    { text: 'Home', icon: <HomeIcon />, path: '/' },
    { text: 'Shorts', icon: <Box component="img" src={ShortsIconPng} alt="Shorts" sx={{ width: 22, height: 22 }} />, path: '/shorts' },
    { text: 'Trending', icon: <WhatshotIcon />, path: '/trending' },
    { text: 'Subscriptions', icon: <SubscriptionsIcon />, path: '/subscriptions' },
    { text: 'Library', icon: <VideoLibraryIcon />, path: '/library' },
    { text: 'History', icon: <HistoryIcon />, path: '/history' },
  ];

  useEffect(() => {
    if (location.pathname === '/') {
      loadInitialVideos();
    }
  }, [location.pathname]);

  const loadInitialVideos = async () => {
    try {
      setLoading(true);
      
      // Fetch initial batch
      let response = await getInitialVideos(0, 50);
      let allVideos = response.videos || [];
      let currentHasMore = response.hasMore;
      let currentOffset = 50;
      
      // Filter for long-form videos
      let longVideos = allVideos.filter(video => {
        if (video.is_short !== undefined) {
          return video.is_short === false;
        }
        if (video.duration && video.duration > 0) {
          return video.duration >= 120;
        }
        return true;
      });
      
      console.log('Batch 1: Total fetched:', allVideos.length, 'Long-form:', longVideos.length);
      
      // Keep fetching until we have at least 12 long videos or run out of data
      while (longVideos.length < 12 && currentHasMore && currentOffset < 200) {
        response = await getInitialVideos(currentOffset, 50);
        const newBatch = response.videos || [];
        
        const newLongVideos = newBatch.filter(video => {
          if (video.is_short !== undefined) return video.is_short === false;
          if (video.duration && video.duration > 0) return video.duration >= 120;
          return true;
        });
        
        longVideos = [...longVideos, ...newLongVideos];
        currentHasMore = response.hasMore;
        currentOffset += 50;
        
        console.log(`Batch ${currentOffset/50}: Fetched ${newBatch.length}, Long-form: ${newLongVideos.length}, Total long: ${longVideos.length}`);
      }
      
      console.log('Final result: Total long-form videos:', longVideos.length);
      
      if (longVideos.length === 0) {
        console.warn('No long-form videos found. All videos are shorts (< 2 minutes).');
        setError('No long-form videos available. All videos are under 2 minutes.');
      }
      
      setVideos(longVideos.slice(0, 12));
      setHasMore(currentHasMore);
      setPage(0);
    } catch (err) {
      setError('Failed to fetch videos.');
      console.error('Videos loading error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = async (query) => {
    try {
      setLoading(true);
      setSearchQuery(query);
      setPage(0);
      setActiveFilter('all'); // Reset filter on new search
      
      if (!query || query.trim() === '') {
        await loadInitialVideos();
        return;
      }
      
      const { results, hasMore: moreAvailable } = await searchVideos(query, 0, 50);
      setAllVideos(results); // Store all results
      setVideos(results); // Display all by default
      setHasMore(moreAvailable);
    } catch (err) {
      setError('Failed to search videos.');
      console.error('Search error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleFilterChange = (filter) => {
    setActiveFilter(filter);
    
    if (filter === 'all') {
      setVideos(allVideos);
    } else if (filter === 'shorts') {
      const shorts = allVideos.filter(video => video.is_short === true);
      setVideos(shorts);
    } else if (filter === 'videos') {
      const longVideos = allVideos.filter(video => video.is_short === false);
      setVideos(longVideos);
    }
  };
  
  const loadMoreVideos = async () => {
    if (loading || loadingMore || !hasMore) return;
    
    try {
      setLoadingMore(true);
      const nextOffset = (page + 1) * 12;
      
      if (searchQuery) {
        const { results, hasMore: moreAvailable } = await searchVideos(searchQuery, nextOffset, 12);
        const longVideos = results.filter(video => {
          if (video.is_short !== undefined) return !video.is_short;
          if (video.duration && video.duration > 0) return video.duration >= 120;
          return true;
        });
        setVideos(prevVideos => {
          const existingIds = new Set(prevVideos.map(v => v.video_id));
          const uniqueResults = longVideos.filter(v => !existingIds.has(v.video_id));
          return [...prevVideos, ...uniqueResults];
        });
        setHasMore(moreAvailable);
      } else {
        const { videos: newVideos, hasMore: moreAvailable } = await getInitialVideos(nextOffset, 12);
        const longVideos = newVideos.filter(video => {
          if (video.is_short !== undefined) return !video.is_short;
          if (video.duration && video.duration > 0) return video.duration >= 120;
          return true;
        });
        setVideos(prevVideos => {
          const existingIds = new Set(prevVideos.map(v => v.video_id));
          const uniqueVideos = longVideos.filter(v => !existingIds.has(v.video_id));
          return [...prevVideos, ...uniqueVideos];
        });
        setHasMore(moreAvailable);
      }
      
      setPage(prevPage => prevPage + 1);
    } catch (err) {
      setError('Failed to load more videos.');
      console.error('Load more error:', err);
    } finally {
      setLoadingMore(false);
    }
  };
  
  useEffect(() => {
    const handleScroll = () => {
      if (
        window.innerHeight + document.documentElement.scrollTop >= 
        document.documentElement.offsetHeight - 500 && 
        !loading && 
        !loadingMore &&
        hasMore &&
        location.pathname === '/'
      ) {
        loadMoreVideos();
      }
    };

    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, [loading, loadingMore, hasMore, page, searchQuery, location.pathname]);

  const handleSidebarItemClick = (path) => {
    navigate(path);
  };

  return (
    <Box sx={{ display: 'flex', minHeight: '100vh', bgcolor: theme.colors.background, transition: 'background-color 0.3s' }}>
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
                    color: location.pathname === item.path ? theme.colors.primary : theme.colors.text,
                    bgcolor: location.pathname === item.path ? theme.colors.primaryHover : 'transparent',
                    fontWeight: location.pathname === item.path ? 700 : 500,
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
                    color: location.pathname === item.path ? theme.colors.primary : theme.colors.textSecondary, 
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
        </>
      )}

      <Box 
        component="main" 
        sx={{ 
          flexGrow: 1, 
          p: { xs: 2, md: 3 },
          mt: '64px',
          ml: !isMobile ? (sidebarOpen ? `${DRAWER_WIDTH}px` : '72px') : 0,
          transition: 'margin 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
          maxWidth: searchQuery ? '1280px' : 'none',
          mx: searchQuery ? 'auto' : 0,
          overflowX: 'hidden',
        }}
      >
        {loading ? (
          <Box display="flex" justifyContent="center" alignItems="center" minHeight="60vh">
            <CircularProgress />
          </Box>
        ) : error ? (
          <Alert severity="error" sx={{ mt: 2 }}>{error}</Alert>
        ) : (
          <>
            {/* Filter Chips - Only show when searching */}
            {searchQuery && (
              <Box sx={{ 
                display: 'flex', 
                gap: 1.5, 
                mb: 3, 
                pb: 2,
                borderBottom: '1px solid #e5e5e5',
                overflowX: 'auto',
                '&::-webkit-scrollbar': { height: 6 },
                '&::-webkit-scrollbar-thumb': { bgcolor: '#ccc', borderRadius: 3 },
              }}>
                <Chip
                  label="All"
                  onClick={() => handleFilterChange('all')}
                  sx={{
                    bgcolor: activeFilter === 'all' ? theme.colors.text : 'transparent',
                    color: activeFilter === 'all' ? theme.colors.surface : theme.colors.text,
                    fontWeight: 500,
                    fontSize: '0.9rem',
                    border: activeFilter === 'all' ? 'none' : `1px solid ${theme.colors.border}`,
                    '&:hover': {
                      bgcolor: activeFilter === 'all' ? theme.colors.text : theme.colors.hover,
                    },
                    cursor: 'pointer',
                    px: 1,
                  }}
                />
                <Chip
                  label="Videos"
                  onClick={() => handleFilterChange('videos')}
                  sx={{
                    bgcolor: activeFilter === 'videos' ? theme.colors.text : 'transparent',
                    color: activeFilter === 'videos' ? theme.colors.surface : theme.colors.text,
                    fontWeight: 500,
                    fontSize: '0.9rem',
                    border: activeFilter === 'videos' ? 'none' : `1px solid ${theme.colors.border}`,
                    '&:hover': {
                      bgcolor: activeFilter === 'videos' ? theme.colors.text : theme.colors.hover,
                    },
                    cursor: 'pointer',
                    px: 1,
                  }}
                />
                <Chip
                  label="Shorts"
                  onClick={() => handleFilterChange('shorts')}
                  sx={{
                    bgcolor: activeFilter === 'shorts' ? theme.colors.text : 'transparent',
                    color: activeFilter === 'shorts' ? theme.colors.surface : theme.colors.text,
                    fontWeight: 500,
                    fontSize: '0.9rem',
                    border: activeFilter === 'shorts' ? 'none' : `1px solid ${theme.colors.border}`,
                    '&:hover': {
                      bgcolor: activeFilter === 'shorts' ? theme.colors.text : theme.colors.hover,
                    },
                    cursor: 'pointer',
                    px: 1,
                  }}
                />
              </Box>
            )}

            <Box sx={{ width: '100%', mx: 0, px: 0, overflowX: 'hidden' }}>
              <Box
                sx={{
                  display: searchQuery ? 'flex' : 'grid',
                  flexDirection: searchQuery ? 'column' : undefined,
                  gridTemplateColumns: searchQuery ? undefined : {
                    xs: '1fr',
                    sm: 'repeat(2, 1fr)',
                    md: 'repeat(3, 1fr)'
                  },
                  gap: searchQuery ? 0 : { xs: 2, md: 3 },
                  alignItems: 'stretch',
                  gridAutoRows: '1fr',
                  width: '100%',
                  maxWidth: '100%',
                }}
              >
                {videos.map((video, index) => {
                  // Use horizontal layout for search results, grid layout for browsing
                  if (searchQuery) {
                    return (
                      <Box key={`${video.video_id}-${index}`} sx={{ width: '100%', maxWidth: '100%' }}>
                        <VideoCardHorizontal video={video} />
                      </Box>
                    );
                  }
                  return (
                    <Box key={`${video.video_id}-${index}`} sx={{ height: '100%' }}>
                      <VideoCard video={video} />
                    </Box>
                  );
                })}
              </Box>
            </Box>

            {loadingMore && (
              <Box display="flex" justifyContent="center" my={4}>
                <CircularProgress />
              </Box>
            )}

            {!loading && !loadingMore && !hasMore && videos.length > 0 && (
              <Box textAlign="center" my={4} color="text.secondary">
                <Typography variant="body1">You've reached the end of the list</Typography>
              </Box>
            )}

            {!loading && !loadingMore && videos.length === 0 && (
              <Box textAlign="center" my={4} color="text.secondary">
                <Typography variant="h6">No videos found</Typography>
              </Box>
            )}
          </>
        )}
      </Box>
    </Box>
  );
};

export default AppContent;
