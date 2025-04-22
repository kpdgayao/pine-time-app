import React from 'react';
import { Box, Paper, Typography, useTheme } from '@mui/material';

interface StatsCardProps {
  title: string;
  value: string | number;
  icon: React.ReactNode;
  color?: 'primary' | 'secondary' | 'success' | 'info' | 'warning';
  trend?: {
    value: number;
    label: string;
  };
}

const StatsCard: React.FC<StatsCardProps> = ({ 
  title, 
  value, 
  icon, 
  color = 'primary',
  trend
}) => {
  const theme = useTheme();
  
  const getColorValue = () => {
    switch (color) {
      case 'primary': return theme.palette.primary.main;
      case 'secondary': return theme.palette.secondary.main;
      case 'success': return theme.palette.success.main;
      case 'info': return theme.palette.info.main;
      case 'warning': return theme.palette.warning.main;
      default: return theme.palette.primary.main;
    }
  };
  
  const getTrendColor = () => {
    if (!trend) return '';
    return trend.value >= 0 ? theme.palette.success.main : theme.palette.error.main;
  };

  return (
    <Paper
      elevation={1}
      sx={{
        p: 2.5,
        borderRadius: 2,
        height: '100%',
        transition: 'transform 0.2s, box-shadow 0.2s',
        '&:hover': {
          transform: 'translateY(-4px)',
          boxShadow: theme.shadows[4],
        }
      }}
    >
      <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
        <Box
          sx={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            width: 48,
            height: 48,
            borderRadius: '50%',
            backgroundColor: `${getColorValue()}20`,
            color: getColorValue(),
            mr: 2
          }}
        >
          {icon}
        </Box>
        <Typography variant="h6" fontWeight="medium" color="text.secondary">
          {title}
        </Typography>
      </Box>
      
      <Typography variant="h4" fontWeight="bold" sx={{ mb: 0.5 }}>
        {value}
      </Typography>
      
      {trend && (
        <Box sx={{ display: 'flex', alignItems: 'center' }}>
          <Typography
            variant="body2"
            sx={{
              color: getTrendColor(),
              fontWeight: 'medium',
              display: 'flex',
              alignItems: 'center',
            }}
          >
            {trend.value >= 0 ? '↑' : '↓'} {Math.abs(trend.value)}%
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ ml: 1 }}>
            {trend.label}
          </Typography>
        </Box>
      )}
    </Paper>
  );
};

export default StatsCard;
