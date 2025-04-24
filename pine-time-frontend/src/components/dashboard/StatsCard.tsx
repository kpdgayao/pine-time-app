import React from 'react';
import { Box, Paper, Typography, useTheme, alpha } from '@mui/material';

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
      elevation={2}
      sx={{
        p: 2.5,
        borderRadius: 2,
        height: '100%',
        position: 'relative',
        overflow: 'hidden',
        transition: 'all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1)',
        borderLeft: `4px solid ${getColorValue()}`,
        '&:hover': {
          transform: 'translateY(-5px)',
          boxShadow: `0 8px 15px -5px ${alpha(getColorValue(), 0.2)}`,
          '& .stats-card-icon': {
            transform: 'scale(1.1) rotate(5deg)',
          }
        },
        '&::before': {
          content: '""',
          position: 'absolute',
          top: 0,
          right: 0,
          width: '30%',
          height: '100%',
          background: `linear-gradient(135deg, transparent 0%, ${alpha(getColorValue(), 0.03)} 100%)`,
          zIndex: 0
        }
      }}
    >
      <Box sx={{ position: 'relative', zIndex: 1 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
          <Box
            className="stats-card-icon"
            sx={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              width: 52,
              height: 52,
              borderRadius: '50%',
              backgroundColor: alpha(getColorValue(), 0.15),
              color: getColorValue(),
              mr: 2,
              boxShadow: `0 4px 8px -2px ${alpha(getColorValue(), 0.2)}`,
              transition: 'transform 0.3s ease'
            }}
          >
            {icon}
          </Box>
          <Typography 
            variant="h6" 
            fontWeight="medium" 
            color="text.secondary"
            sx={{ 
              letterSpacing: '0.5px',
              fontSize: '1rem'
            }}
          >
            {title}
          </Typography>
        </Box>
        
        <Typography 
          variant="h4" 
          fontWeight="bold" 
          sx={{ 
            mb: 0.5,
            color: theme.palette.text.primary,
            fontSize: { xs: '1.75rem', sm: '2rem' }
          }}
        >
          {value}
        </Typography>
        
        {trend && (
          <Box 
            sx={{ 
              display: 'flex', 
              alignItems: 'center',
              mt: 1,
              p: 0.75,
              borderRadius: 1,
              width: 'fit-content',
              backgroundColor: alpha(getTrendColor(), 0.1)
            }}
          >
            <Typography
              variant="body2"
              sx={{
                color: getTrendColor(),
                fontWeight: 'bold',
                display: 'flex',
                alignItems: 'center',
                fontSize: '0.75rem'
              }}
            >
              {trend.value >= 0 ? '↑' : '↓'} {Math.abs(trend.value)}%
            </Typography>
            <Typography 
              variant="body2" 
              color="text.secondary" 
              sx={{ 
                ml: 1,
                fontSize: '0.75rem',
                opacity: 0.8
              }}
            >
              {trend.label}
            </Typography>
          </Box>
        )}
      </Box>
    </Paper>
  );
};

export default StatsCard;
