import React, { useState, useEffect } from 'react';
import { Box, Typography, Tooltip, Paper, LinearProgress, useTheme, alpha, Fade } from '@mui/material';
import { Badge } from '../types/badges';
import EmojiEventsIcon from '@mui/icons-material/EmojiEvents';
import ArrowUpwardIcon from '@mui/icons-material/ArrowUpward';

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
  const [showNextLevelHint, setShowNextLevelHint] = useState(false);
  
  // Pine Time green theme color (from user rules)
  const pineTimeGreen = '#2E7D32';
  
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
    }, 300);
    
    return () => clearTimeout(timer);
  }, [badge.progress, animate]);

  const progressPercentage = badge.next_level_threshold 
    ? Math.min(100, (progress / badge.next_level_threshold) * 100) 
    : 100;
  
  const tooltipContent = badge.next_level_threshold 
    ? `Progress: ${progress}/${badge.next_level_threshold} (${Math.round(progressPercentage)}%)`
    : 'Maximum level achieved!';
    
  // Get badge level color based on level
  const getBadgeLevelColor = () => {
    if (!badge.level) return pineTimeGreen;
    
    switch (badge.level) {
      case 1: return pineTimeGreen; // Pine Time green for level 1
      case 2: return '#1976D2'; // Blue for level 2
      case 3: return '#7B1FA2'; // Purple for level 3
      case 4: return '#C62828'; // Red for level 4
      case 5: return '#F57C00'; // Orange for level 5
      default: return pineTimeGreen;
    }
  };
  
  // Get badge level name
  const getBadgeLevelName = () => {
    if (!badge.level) return 'Bronze';
    
    switch (badge.level) {
      case 1: return 'Bronze';
      case 2: return 'Silver';
      case 3: return 'Gold';
      case 4: return 'Platinum';
      case 5: return 'Diamond';
      default: return 'Bronze';
    }
  };

  return (
    <Tooltip 
      title={showTooltip ? tooltipContent : ''} 
      arrow 
      placement="top"
    >
      <Paper 
        elevation={2} 
        sx={{ 
          p: 2.5, 
          borderRadius: 2, 
          mb: 2,
          position: 'relative',
          overflow: 'hidden',
          transition: 'all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1)',
          borderLeft: `4px solid ${getBadgeLevelColor()}`,
          '&:hover': {
            transform: 'translateY(-3px)',
            boxShadow: `0 8px 15px -5px ${alpha(getBadgeLevelColor(), 0.25)}`,
            '& .next-level-hint': {
              opacity: 1,
              transform: 'translateY(0)'
            }
          },
          '&::before': {
            content: '""',
            position: 'absolute',
            top: 0,
            right: 0,
            width: '25%',
            height: '100%',
            background: `linear-gradient(135deg, transparent 0%, ${alpha(getBadgeLevelColor(), 0.03)} 100%)`,
            zIndex: 0
          }
        }}
        onMouseEnter={() => setShowNextLevelHint(true)}
        onMouseLeave={() => setShowNextLevelHint(false)}
      >
        <Box sx={{ position: 'relative', zIndex: 1 }}>
          {/* Badge Header */}
          <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1.5, alignItems: 'center' }}>
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              <Box
                sx={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  width: 36,
                  height: 36,
                  borderRadius: '50%',
                  backgroundColor: alpha(getBadgeLevelColor(), 0.15),
                  color: getBadgeLevelColor(),
                  mr: 1.5,
                  boxShadow: `0 4px 8px -2px ${alpha(getBadgeLevelColor(), 0.2)}`,
                }}
              >
                <EmojiEventsIcon fontSize="small" />
              </Box>
              
              <Box>
                <Typography variant="subtitle1" fontWeight="bold" sx={{ lineHeight: 1.2 }}>
                  {badge.name}
                </Typography>
                <Typography variant="caption" color="text.secondary" sx={{ display: 'block' }}>
                  {badge.category || 'Achievement'}
                </Typography>
              </Box>
            </Box>
            
            {badge.level && (
              <Box 
                sx={{ 
                  px: 1.5, 
                  py: 0.5, 
                  borderRadius: 1.5, 
                  backgroundColor: alpha(getBadgeLevelColor(), 0.15), 
                  color: getBadgeLevelColor(),
                  display: 'flex',
                  alignItems: 'center',
                  fontWeight: 'bold',
                  fontSize: '0.75rem',
                  boxShadow: `0 2px 4px ${alpha(getBadgeLevelColor(), 0.15)}`
                }}
              >
                {getBadgeLevelName()} {badge.level}
              </Box>
            )}
          </Box>
          
          {/* Badge Description */}
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            {badge.description}
          </Typography>
          
          {/* Progress Section */}
          <Box sx={{ position: 'relative' }}>
            {/* Progress Bar */}
            <Box sx={{ position: 'relative', mb: 0.5 }}>
              <LinearProgress 
                variant="determinate" 
                value={progressPercentage} 
                sx={{ 
                  height: 10, 
                  borderRadius: 5,
                  backgroundColor: alpha(getBadgeLevelColor(), 0.15),
                  '& .MuiLinearProgress-bar': {
                    transition: animate ? 'transform 1.5s cubic-bezier(0.65, 0, 0.35, 1)' : 'none',
                    backgroundImage: `linear-gradient(90deg, ${alpha(getBadgeLevelColor(), 0.8)} 0%, ${getBadgeLevelColor()} 100%)`,
                    boxShadow: `0 0 8px ${alpha(getBadgeLevelColor(), 0.5)}`
                  }
                }}
              />
              
              {/* Progress Markers */}
              {badge.next_level_threshold && (
                <Box sx={{ 
                  position: 'absolute', 
                  top: 0, 
                  left: 0, 
                  width: '100%', 
                  height: '100%', 
                  pointerEvents: 'none' 
                }}>
                  {/* 25% Marker */}
                  <Box sx={{ 
                    position: 'absolute', 
                    left: '25%', 
                    top: -2, 
                    height: 14, 
                    width: 1, 
                    backgroundColor: alpha(theme.palette.text.secondary, 0.3) 
                  }} />
                  
                  {/* 50% Marker */}
                  <Box sx={{ 
                    position: 'absolute', 
                    left: '50%', 
                    top: -2, 
                    height: 14, 
                    width: 1, 
                    backgroundColor: alpha(theme.palette.text.secondary, 0.3) 
                  }} />
                  
                  {/* 75% Marker */}
                  <Box sx={{ 
                    position: 'absolute', 
                    left: '75%', 
                    top: -2, 
                    height: 14, 
                    width: 1, 
                    backgroundColor: alpha(theme.palette.text.secondary, 0.3) 
                  }} />
                </Box>
              )}
            </Box>
            
            {/* Progress Text */}
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <Typography variant="caption" color="text.secondary" fontWeight="medium">
                {progress} points
              </Typography>
              
              {badge.next_level_threshold && (
                <Typography variant="caption" color="text.secondary" fontWeight="medium">
                  Next level: {badge.next_level_threshold} points
                </Typography>
              )}
            </Box>
            
            {/* Next Level Hint - Animated */}
            {badge.next_level_threshold && badge.next_level && (
              <Fade in={showNextLevelHint}>
                <Box 
                  className="next-level-hint"
                  sx={{ 
                    mt: 2,
                    p: 1.5,
                    borderRadius: 1,
                    backgroundColor: alpha(getBadgeLevelColor(), 0.08),
                    border: `1px dashed ${alpha(getBadgeLevelColor(), 0.3)}`,
                    display: 'flex',
                    alignItems: 'center',
                    gap: 1,
                    opacity: 0,
                    transform: 'translateY(10px)',
                    transition: 'opacity 0.3s ease, transform 0.3s ease',
                  }}
                >
                  <ArrowUpwardIcon fontSize="small" sx={{ color: getBadgeLevelColor() }} />
                  <Typography variant="caption" sx={{ color: 'text.secondary', fontStyle: 'italic' }}>
                    <strong>Next Level:</strong> {badge.next_level_name || `${getBadgeLevelName()} ${(badge.level || 0) + 1}`} - 
                    {badge.next_level_description || `Need ${badge.next_level_threshold - (badge.progress || 0)} more points`}
                  </Typography>
                </Box>
              </Fade>
            )}
          </Box>
        </Box>
      </Paper>
    </Tooltip>
  );
};

export default BadgeProgressBar;
