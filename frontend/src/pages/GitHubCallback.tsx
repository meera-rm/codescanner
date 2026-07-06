import React, { useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { Container, CircularProgress, Typography, Alert } from '@mui/material';

const GitHubCallback: React.FC = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [error, setError] = React.useState<string | null>(null);

  useEffect(() => {
    const handleCallback = async () => {
      try {
        const code = searchParams.get('code');
        const state = searchParams.get('state');

        if (!code) {
          setError('No authorization code received from GitHub');
          return;
        }

        // Exchange code for access token
        const response = await fetch('/api/v1/github/authorize', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ code, state }),
        });

        if (!response.ok) {
          const error = await response.json();
          throw new Error(error.detail || 'Failed to authorize');
        }

        const data = await response.json();

        // Save user info and token
        localStorage.setItem('github_access_token', data.access_token);
        localStorage.setItem('github_user', JSON.stringify(data.user));
        localStorage.setItem('userId', data.user.id);

        // Redirect to GitHub connect page
        navigate('/github-connect');
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Authorization failed');
      }
    };

    handleCallback();
  }, [searchParams, navigate]);

  if (error) {
    return (
      <Container maxWidth="sm" sx={{ py: 8, textAlign: 'center' }}>
        <Alert severity="error">
          <Typography variant="h6" sx={{ mb: 2 }}>
            Authorization Failed
          </Typography>
          <Typography variant="body2">{error}</Typography>
        </Alert>
      </Container>
    );
  }

  return (
    <Container maxWidth="sm" sx={{ py: 8, textAlign: 'center' }}>
      <CircularProgress sx={{ mb: 3 }} />
      <Typography variant="h6">Authorizing with GitHub...</Typography>
      <Typography variant="body2" sx={{ color: '#666', mt: 2 }}>
        Please wait while we complete the authorization process.
      </Typography>
    </Container>
  );
};

export default GitHubCallback;
