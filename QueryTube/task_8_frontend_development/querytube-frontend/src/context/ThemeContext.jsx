import React, { createContext, useContext, useState, useEffect } from 'react';

const ThemeContext = createContext();

export const useTheme = () => {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within ThemeProvider');
  }
  return context;
};

export const ThemeProvider = ({ children }) => {
  const [darkMode, setDarkMode] = useState(() => {
    const saved = localStorage.getItem('darkMode');
    return saved ? JSON.parse(saved) : false;
  });

  useEffect(() => {
    localStorage.setItem('darkMode', JSON.stringify(darkMode));
  }, [darkMode]);

  const toggleTheme = () => {
    setDarkMode(prev => !prev);
  };

  const theme = {
    darkMode,
    toggleTheme,
    colors: darkMode ? {
      // Dark mode colors
      background: '#0f0f0f',
      surface: '#212121',
      card: '#1e1e1e',
      text: '#f1f1f1',
      textSecondary: '#aaaaaa',
      border: '#303030',
      hover: '#2a2a2a',
      navbar: '#0f0f0f',
      primary: '#ff0000',
      primaryHover: 'rgba(255, 0, 0, 0.1)',
    } : {
      // Light mode colors
      background: '#f9f9f9',
      surface: '#ffffff',
      card: '#ffffff',
      text: '#0f0f0f',
      textSecondary: '#606060',
      border: '#e5e5e5',
      hover: 'rgba(0, 0, 0, 0.04)',
      navbar: '#ffffff',
      primary: '#ff0000',
      primaryHover: 'rgba(255, 0, 0, 0.08)',
    }
  };

  return (
    <ThemeContext.Provider value={theme}>
      {children}
    </ThemeContext.Provider>
  );
};
