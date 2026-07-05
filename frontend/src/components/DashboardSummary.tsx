import React from 'react';
import { Grid, Paper, Typography, Box } from '@mui/material';
import {
  TrendingUp,
  AlertCircle,
  Activity,
  Zap,
} from 'lucide-react';

interface SummaryProps {
  summary: {
    ai_insights: {
      total_patterns: number;
      avg_complexity: number;
      improvements_recommended: number;
    };
    enterprise: {
      plan: string;
      active_api_keys: number;
      usage_percentage: number;
    };
    monitoring: {
      health: number;
      error_rate: number;
      response_time_ms: number;
      active_alerts: number;
    };
    activity: {
      recent_analyses: number;
      github_prs: number;
      ide_plugins: number;
    };
  };
}

const DashboardSummary: React.FC<SummaryProps> = ({ summary }) => {
  const cards = [
    {
      label: 'System Health',
      value: `${summary.monitoring.health.toFixed(1)}%`,
      icon: Activity,
      color: '#4CAF50',
      subtitle: `${summary.monitoring.active_alerts} alerts`,
    },
    {
      label: 'API Health',
      value: `${(100 - summary.monitoring.error_rate).toFixed(1)}%`,
      icon: TrendingUp,
      color: '#2196F3',
      subtitle: `${summary.monitoring.error_rate.toFixed(2)}% error rate`,
    },
    {
      label: 'Patterns Found',
      value: summary.ai_insights.total_patterns,
      icon: Zap,
      color: '#FF9800',
      subtitle: `Avg complexity: ${summary.ai_insights.avg_complexity.toFixed(1)}`,
    },
    {
      label: 'Plan Usage',
      value: `${summary.enterprise.usage_percentage.toFixed(0)}%`,
      icon: AlertCircle,
      color: '#9C27B0',
      subtitle: `Plan: ${summary.enterprise.plan.toUpperCase()}`,
    },
  ];

  return (
    <Grid container spacing={2}>
      {cards.map((card, idx) => {
        const Icon = card.icon;
        return (
          <Grid item xs={12} sm={6} md={3} key={idx}>
            <Paper
              sx={{
                p: 3,
                background: 'linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%)',
                borderLeft: `4px solid ${card.color}`,
                cursor: 'pointer',
                transition: 'transform 0.2s',
                '&:hover': {
                  transform: 'translateY(-4px)',
                },
              }}
            >
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <div>
                  <Typography variant="caption" sx={{ color: '#666' }}>
                    {card.label}
                  </Typography>
                  <Typography variant="h5" sx={{ fontWeight: 'bold', mt: 1, color: '#000' }}>
                    {card.value}
                  </Typography>
                  <Typography variant="caption" sx={{ color: '#999', display: 'block', mt: 0.5 }}>
                    {card.subtitle}
                  </Typography>
                </div>
                <Icon size={32} color={card.color} />
              </Box>
            </Paper>
          </Grid>
        );
      })}
    </Grid>
  );
};

export default DashboardSummary;
