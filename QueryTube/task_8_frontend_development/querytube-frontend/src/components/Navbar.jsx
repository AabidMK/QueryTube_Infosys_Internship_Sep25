
import React, { useState } from 'react';
import QueryTubeLogo from '../assets/QueryTube.png';
import {
  AppBar,
  Box,
  Toolbar,
  IconButton,
  Typography,
  Avatar,
  Menu,
  MenuItem,
  Switch,
  ListItemIcon,
  ListItemText,
} from '@mui/material';
import MenuIcon from '@mui/icons-material/Menu';
import VideoCallIcon from '@mui/icons-material/VideoCall';
import NotificationsIcon from '@mui/icons-material/Notifications';
import DarkModeIcon from '@mui/icons-material/DarkMode';
import LightModeIcon from '@mui/icons-material/LightMode';
import SearchBar from './SearchBar';
import { useTheme } from '../context/ThemeContext';

const Navbar = ({ onSearch, sidebarOpen, setSidebarOpen }) => {
  const theme = useTheme();
  const [anchorEl, setAnchorEl] = useState(null);
  const open = Boolean(anchorEl);

  const handleMenuClick = () => {
    setSidebarOpen(!sidebarOpen);
  };

  const handleAvatarClick = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleClose = () => {
    setAnchorEl(null);
  };

  const handleThemeToggle = () => {
    theme.toggleTheme();
  };

  return (
    <AppBar position="fixed" elevation={0} sx={{ bgcolor: theme.colors.navbar, borderBottom: `1px solid ${theme.colors.border}`, zIndex: 1500, transition: 'background-color 0.3s, border-color 0.3s' }}>
      <Toolbar sx={{ minHeight: 64, px: { xs: 1, sm: 2 }, justifyContent: 'space-between' }}>
        {/* Left: Hamburger + Logo */}
        <Box sx={{ display: 'flex', alignItems: 'center', minWidth: 180 }}>
          <IconButton size="large" edge="start" color="inherit" aria-label="menu" sx={{ mr: 1, color: theme.colors.primary, '&:hover': { bgcolor: theme.colors.primaryHover } }} onClick={handleMenuClick}>
            <MenuIcon sx={{ fontSize: 28, color: theme.colors.text }} />
          </IconButton>
          <a href="/" style={{ textDecoration: 'none', display: 'flex', alignItems: 'center', ml: 4 }}>
            <Box
              component="img"
              src={QueryTubeLogo}
              alt="QueryTube"
              sx={{ height: 28, mr: 1, display: { xs: 'none', sm: 'block' }, cursor: 'pointer' }}
            />
            <Typography
              variant="h6"
              component="div"
              sx={{
                color: theme.colors.primary,
                fontWeight: 700,
                fontFamily: 'Roboto, Arial, sans-serif',
                letterSpacing: '-0.5px',
                fontSize: '1.4rem',
                display: 'flex',
                alignItems: 'center',
                userSelect: 'none',
              }}
            >
              QueryTube
            </Typography>
          </a>
        </Box>

        {/* Center: SearchBar */}
        <Box sx={{ flex: 1, display: 'flex', justifyContent: 'center', px: 2 }}>
          <Box sx={{ width: { xs: '100%', sm: 480, md: 600 }, maxWidth: '100%' }}>
            <SearchBar onSearch={onSearch} />
          </Box>
        </Box>

        {/* Right: Icons */}
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, minWidth: 120, justifyContent: 'flex-end' }}>
          <IconButton color="default" sx={{ p: 1, color: theme.colors.text }}>
            <VideoCallIcon sx={{ fontSize: 26 }} />
          </IconButton>
          <IconButton color="default" sx={{ p: 1, color: theme.colors.text }}>
            <NotificationsIcon sx={{ fontSize: 26 }} />
          </IconButton>
          <IconButton onClick={handleAvatarClick}>
            <Avatar sx={{ width: 32, height: 32, bgcolor: theme.colors.border, color: theme.colors.text, fontWeight: 600, fontSize: 18, cursor: 'pointer' }}>U</Avatar>
          </IconButton>
        </Box>

        {/* User Menu */}
        <Menu
          anchorEl={anchorEl}
          open={open}
          onClose={handleClose}
          anchorOrigin={{
            vertical: 'bottom',
            horizontal: 'right',
          }}
          transformOrigin={{
            vertical: 'top',
            horizontal: 'right',
          }}
          PaperProps={{
            sx: {
              bgcolor: theme.colors.surface,
              color: theme.colors.text,
              mt: 1,
              minWidth: 200,
              borderRadius: 2,
              boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
            }
          }}
        >
          <MenuItem onClick={handleThemeToggle} sx={{ py: 1.5, '&:hover': { bgcolor: theme.colors.hover } }}>
            <ListItemIcon sx={{ color: theme.colors.text }}>
              {theme.darkMode ? <LightModeIcon /> : <DarkModeIcon />}
            </ListItemIcon>
            <ListItemText primary={theme.darkMode ? 'Light Mode' : 'Dark Mode'} />
            <Switch
              checked={theme.darkMode}
              onChange={handleThemeToggle}
              size="small"
              sx={{
                '& .MuiSwitch-switchBase.Mui-checked': {
                  color: theme.colors.primary,
                },
                '& .MuiSwitch-switchBase.Mui-checked + .MuiSwitch-track': {
                  backgroundColor: theme.colors.primary,
                },
              }}
            />
          </MenuItem>
        </Menu>
      </Toolbar>
    </AppBar>
  );
};

export default Navbar;