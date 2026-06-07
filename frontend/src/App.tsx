import React from 'react';
import ErrorBoundary from './components/ErrorBoundary';
import { CAQIDashboard } from './pages/CAQIDashboard';

const App: React.FC = () => {
  return (
    <ErrorBoundary>
      <CAQIDashboard />
    </ErrorBoundary>
  );
};

export default App;
