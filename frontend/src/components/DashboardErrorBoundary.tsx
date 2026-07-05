/**
 * Dashboard Error Boundary
 * Catches errors in dashboard and displays graceful error UI
 */

import React, { ReactNode, ErrorInfo } from 'react';

interface Props {
  children: ReactNode;
  fallback?: (error: Error, retry: () => void) => ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

class DashboardErrorBoundary extends React.Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('Dashboard Error:', error, errorInfo);
  }

  retry = () => {
    this.setState({ hasError: false, error: null });
  };

  render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback(this.state.error!, this.retry);
      }

      return (
        <div className="error-boundary-container">
          <div className="error-content">
            <h2>⚠️ Dashboard Error</h2>
            <p className="error-message">{this.state.error?.message || 'Unknown error occurred'}</p>
            <details className="error-details">
              <summary>Technical Details</summary>
              <pre>{this.state.error?.stack}</pre>
            </details>
            <button onClick={this.retry} className="retry-button">
              🔄 Retry
            </button>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

export default DashboardErrorBoundary;
