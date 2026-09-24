import React, { useEffect, useState } from 'react';
import { Paper, Typography, Box, List, ListItem } from '@mui/material';
import { Brain } from 'lucide-react';

const AIInsightsWidget: React.FC = () => {
  const [insights, setInsights] = useState({
    total_patterns: 0,
    avg_complexity: 0,
    top_agents: [],
  });

  useEffect(() => {
    fetchInsights();
  }, []);

  const fetchInsights = async () => {
    try {
      const response = await fetch('/api/v1/dashboard/widgets/ai-insights', {
        headers: {
          'X-API-Key': localStorage.getItem('apiKey') || '',
        },
      });
      const data = await response.json();
      setInsights(data.data);
    } catch (err) {
      console.error('Failed to fetch insights:', err);
    }
  };

  return (
    <Paper
      sx={{
        p: 3,
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        color: 'white',
        borderRadius: '12px',
      }}
    >
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
        <Brain size={28} />
        <Typography variant="h6" sx={{ fontWeight: 'bold' }}>
          AI Learning Insights
        </Typography>
      </Box>

      <Box sx={{ mb: 2 }}>
        <Typography variant="body2" sx={{ opacity: 0.9 }}>
          Total Patterns Analyzed
        </Typography>
        <Typography variant="h4" sx={{ fontWeight: 'bold', mt: 0.5 }}>
          {insights.total_patterns}
        </Typography>
      </Box>

      <Box sx={{ mb: 2 }}>
        <Typography variant="body2" sx={{ opacity: 0.9 }}>
          Average Complexity
        </Typography>
        <Typography variant="h6" sx={{ mt: 0.5 }}>
          {insights.avg_complexity.toFixed(1)}
        </Typography>
      </Box>

      <Typography variant="subtitle2" sx={{ mb: 1, opacity: 0.9 }}>
        Top Performing Agents
      </Typography>
      <List sx={{ p: 0 }}>
        {insights.top_agents.map((agent: any, idx) => (
          <ListItem key={idx} sx={{ p: 0.5, display: 'flex', justifyContent: 'space-between' }}>
            <Typography variant="body2">{agent.name}</Typography>
            <Typography variant="body2" sx={{ fontWeight: 'bold' }}>
              {(agent.accuracy * 100).toFixed(0)}%
            </Typography>
          </ListItem>
        ))}
      </List>
    </Paper>
  );
};

export default AIInsightsWidget;
