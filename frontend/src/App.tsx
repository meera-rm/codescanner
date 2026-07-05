import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import ErrorBoundary from './components/ErrorBoundary';
import Home from './pages/Home';
import { CAQILanding } from './pages/CAQILanding';
import { CAQIDashboard } from './pages/CAQIDashboard';
import { CAQIAnalyzer } from './pages/CAQIAnalyzer';
import PersonalityProfiler from './pages/PersonalityProfiler';
import InheritanceLetter from './pages/InheritanceLetter';
import CodeScanner from './pages/CodeScanner';
import OnboardingProfiles from './pages/OnboardingProfiles';
import APIDocumentation from './pages/APIDocumentation';
import IterationDashboard from './pages/IterationDashboard';

const App: React.FC = () => {
  return (
    <ErrorBoundary>
      <Router>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/personality" element={<PersonalityProfiler />} />
          <Route path="/letter" element={<InheritanceLetter />} />
          <Route path="/caqi" element={<CAQILanding />} />
          <Route path="/caqi/analyzer" element={<CAQIAnalyzer />} />
          <Route path="/caqi/dashboard" element={<CAQIDashboard />} />
          <Route path="/scanner" element={<CodeScanner />} />
          <Route path="/onboarding" element={<OnboardingProfiles />} />
          <Route path="/api" element={<APIDocumentation />} />
          <Route path="/dashboard/:jobId" element={<IterationDashboard />} />
          <Route path="/iteration/:jobId" element={<IterationDashboard />} />
        </Routes>
      </Router>
    </ErrorBoundary>
  );
};

export default App;
