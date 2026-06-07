import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import ErrorBoundary from './components/ErrorBoundary';
import Home from './pages/Home';
import { CAQIDashboard } from './pages/CAQIDashboard';
import PersonalityProfiler from './pages/PersonalityProfiler';
import InheritanceLetter from './pages/InheritanceLetter';
import CodeScanner from './pages/CodeScanner';
import OnboardingProfiles from './pages/OnboardingProfiles';
import APIDocumentation from './pages/APIDocumentation';

const App: React.FC = () => {
  return (
    <ErrorBoundary>
      <Router>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/personality" element={<PersonalityProfiler />} />
          <Route path="/letter" element={<InheritanceLetter />} />
          <Route path="/caqi" element={<CAQIDashboard />} />
          <Route path="/scanner" element={<CodeScanner />} />
          <Route path="/onboarding" element={<OnboardingProfiles />} />
          <Route path="/api" element={<APIDocumentation />} />
        </Routes>
      </Router>
    </ErrorBoundary>
  );
};

export default App;
