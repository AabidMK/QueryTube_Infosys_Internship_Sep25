import React, { useState } from 'react';
import { Paper, InputBase, IconButton } from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';
import { useTheme } from '../context/ThemeContext';

const SearchBar = ({ onSearch }) => {
  const theme = useTheme();
  const [query, setQuery] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (query.trim()) {
      onSearch(query);
    }
  };

  return (
    <Paper
      component="form"
      onSubmit={handleSubmit}
      elevation={0}
      sx={{
        display: 'flex',
        alignItems: 'center',
        width: '100%',
        maxWidth: 600,
        borderRadius: 10,
        border: `1.5px solid ${theme.colors.border}`,
        boxShadow: theme.darkMode ? '0 1.5px 8px 0 rgba(0,0,0,.3)' : '0 1.5px 8px 0 rgba(60,64,67,.04)',
        px: 1.5,
        py: 0.5,
        bgcolor: theme.colors.surface,
        transition: 'all 0.3s',
      }}
    >
      <InputBase
        sx={{ 
          ml: 1, 
          flex: 1, 
          fontSize: 16, 
          fontFamily: 'Roboto, Arial, sans-serif',
          color: theme.colors.text,
          '& ::placeholder': {
            color: theme.colors.textSecondary,
            opacity: 1,
          },
        }}
        placeholder="Search for YouTube videos..."
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        inputProps={{ 'aria-label': 'search youtube videos' }}
      />
      <IconButton type="submit" sx={{ p: '10px', color: theme.colors.text }}>
        <SearchIcon />
      </IconButton>
    </Paper>
  );
};

export default SearchBar;