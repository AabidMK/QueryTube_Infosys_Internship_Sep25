import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import AppContent from './AppContent';
import ShortsPage from './components/ShortsPage';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<AppContent />} />
        <Route path="/shorts" element={<ShortsPage />} />
      </Routes>
    </Router>
  );
}

export default App;
