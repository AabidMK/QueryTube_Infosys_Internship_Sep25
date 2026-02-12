import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider } from './context/ThemeContext';
import AppContent from './AppContent';
import ShortsPage from './components/ShortsPage';
import VideoPlayer from './components/VideoPlayer';

function App() {
  return (
    <ThemeProvider>
      <Router>
        <Routes>
          <Route path="/" element={<AppContent />} />
          <Route path="/shorts" element={<ShortsPage />} />
          <Route path="/watch/:videoId" element={<VideoPlayer />} />
        </Routes>
      </Router>
    </ThemeProvider>
  );
}

export default App;
