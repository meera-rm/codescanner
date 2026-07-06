import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import './styles/global-dark-mode.css';
import ErrorBoundary from './components/ErrorBoundary';
import Home from './pages/Home';
import Dashboard from './pages/Dashboard';
import SecurityDashboard from './pages/SecurityDashboard';
import { CAQILanding } from './pages/CAQILanding';
import { CAQIDashboard } from './pages/CAQIDashboard';
import { CAQIAnalyzer } from './pages/CAQIAnalyzer';
import PersonalityProfiler from './pages/PersonalityProfiler';
import InheritanceLetter from './pages/InheritanceLetter';
import CodeScanner from './pages/CodeScanner';
import OnboardingProfiles from './pages/OnboardingProfiles';
import APIDocumentation from './pages/APIDocumentation';
import IterationDashboard from './pages/IterationDashboard';
import GitHubConnect from './pages/GitHubConnect';
import GitHubCallback from './pages/GitHubCallback';
import CIDashboard from './pages/CIDashboard';
import MonitoringDashboard from './pages/MonitoringDashboard';

const App: React.FC = () => {
  return (
    <ErrorBoundary>
      <Router>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/ci-dashboard" element={<CIDashboard />} />
          <Route path="/monitoring" element={<MonitoringDashboard />} />
          <Route path="/security-dashboard" element={<SecurityDashboard />} />
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
          <Route path="/github-connect" element={<GitHubConnect />} />
          <Route path="/github-callback" element={<GitHubCallback />} />
        </Routes>
      </Router>
    </ErrorBoundary>
  );
};

export default App;
