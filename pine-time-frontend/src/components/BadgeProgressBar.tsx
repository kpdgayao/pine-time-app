import React, { useState, useEffect } from 'react';
import { Box, Typography, Tooltip, Paper, LinearProgress, useTheme } from '@mui/material';
import { Badge } from '../types/badges';

interface BadgeProgressBarProps {
  badge: Badge;
  showTooltip?: boolean;
  animate?: boolean;
}

const BadgeProgressBar: React.FC<BadgeProgressBarProps> = ({ 
  badge, 
  showTooltip = true,
  animate = true 
}) => {
  const theme = useTheme();
  const [progress, setProgress] = useState(0);
  
  // Animation effect for progress bar
  useEffect(() => {
    if (!animate) {
      setProgress(badge.progress || 0);
      return;
    }
    
    // Start with 0 and animate to the actual value
    setProgress(0);
    const timer = setTimeout(() => {
      setProgress(badge.progress || 0);
    }, 200);
    
    return () => clearTimeout(timer);
  }, [badge.progress, animate]);

  const progressPercentage = badge.next_level_threshold 
    ? Math.min(100, (progress / badge.next_level_threshold) * 100) 
    : 100;
  
  const tooltipContent = badge.next_level_threshold 
    ? `Progress: ${progress}/${badge.next_level_threshold} (${Math.round(progressPercentage)}%)`
    : 'Maximum level achieved!';

  return (
    <Tooltip 
      title={showTooltip ? tooltipContent : ''} 
      arrow 
      placement="top"
    >
      <Paper 
        elevation={1} 
        sx={{ 
          p: 2, 
          borderRadius: 2, 
          mb: 1.5,
          transition: 'transform 0.2s, box-shadow 0.2s',
          '&:hover': {
            transform: 'translateY(-2px)',
            boxShadow: theme.shadows[3],
          }
        }}
      >
        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
          <Typography variant="subtitle1" fontWeight="bold">
            {badge.name}
            {badge.level && (
              <Typography 
                component="span" 
                sx={{ 
                  ml: 1, 
                  px: 1, 
                  py: 0.2, 
                  borderRadius: 1, 
                  backgroundColor: theme.palette.primary.main, 
                  color: theme.palette.primary.contrastText,
                  fontSize: '0.75rem'
                }}
              >
                Level {badge.level}
              </Typography>
            )}
          </Typography>
          {badge.next_level_threshold && (
            <Typography variant="body2" color="text.secondary">
              {progress}/{badge.next_level_threshold}
            </Typography>
          )}
        </Box>
        
        <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
          {badge.description}
        </Typography>
        
        <LinearProgress 
          variant="determinate" 
          value={progressPercentage} 
          sx={{ 
            height: 8, 
            borderRadius: 4,
            '& .MuiLinearProgress-bar': {
              transition: animate ? 'transform 1.5s ease-in-out' : 'none'
            }
          }} 
          color={badge.level && badge.level >= 3 ? "secondary" : "primary"}
        />
      </Paper>
    </Tooltip>
  );
};

export default BadgeProgressBar;
