import React from 'react';
import { Box, Typography, Paper, useTheme, alpha, Tooltip } from '@mui/material';
import EmojiEventsIcon from '@mui/icons-material/EmojiEvents';
import StarIcon from '@mui/icons-material/Star';
import LocalFireDepartmentIcon from '@mui/icons-material/LocalFireDepartment';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';

interface MilestoneApproachIndicatorProps {
  type: 'badge' | 'points' | 'streak' | 'rank';
  currentValue: number;
  targetValue: number;
  label: string;
  description?: string;
}

const MilestoneApproachIndicator: React.FC<MilestoneApproachIndicatorProps> = ({
  type,
  currentValue,
  targetValue,
  label,
  description
}) => {
  const theme = useTheme();
  
  // Pine Time green theme color
  const pineTimeGreen = '#2E7D32';
  
  // Calculate progress percentage
  const progressPercentage = Math.min(100, (currentValue / targetValue) * 100);
  
  // Determine if close to milestone (within 90%)
  const isCloseToMilestone = progressPercentage >= 90;
  
  // Get icon and color based on milestone type
  const getIconAndColor = () => {
    switch (type) {
      case 'badge':
        return { 
          icon: <EmojiEventsIcon />, 
          color: theme.palette.secondary.main,
          gradientStart: theme.palette.secondary.light,
          gradientEnd: theme.palette.secondary.dark
        };
      case 'points':
        return { 
          icon: <StarIcon />, 
          color: theme.palette.primary.main,
          gradientStart: theme.palette.primary.light,
          gradientEnd: theme.palette.primary.dark
        };
      case 'streak':
        return { 
          icon: <LocalFireDepartmentIcon />, 
          color: theme.palette.warning.main,
          gradientStart: theme.palette.warning.light,
          gradientEnd: theme.palette.warning.dark
        };
      case 'rank':
        return { 
          icon: <TrendingUpIcon />, 
          color: pineTimeGreen,
          gradientStart: '#4CAF50',
          gradientEnd: '#1B5E20'
        };
      default:
        return { 
          icon: <StarIcon />, 
          color: pineTimeGreen,
          gradientStart: '#4CAF50',
          gradientEnd: '#1B5E20'
        };
    }
  };
  
  const { icon, color, gradientStart, gradientEnd } = getIconAndColor();
  
  // Determine animation style based on proximity to milestone
  const getAnimationStyle = () => {
    if (progressPercentage >= 95) {
      return {
        animation: 'pulse-strong 1.5s infinite',
        '@keyframes pulse-strong': {
          '0%': { transform: 'scale(1)', boxShadow: `0 0 0 0 ${alpha(color, 0.7)}` },
          '70%': { transform: 'scale(1.05)', boxShadow: `0 0 0 10px ${alpha(color, 0)}` },
          '100%': { transform: 'scale(1)', boxShadow: `0 0 0 0 ${alpha(color, 0)}` },
        }
      };
    } else if (progressPercentage >= 90) {
      return {
        animation: 'pulse-medium 2s infinite',
        '@keyframes pulse-medium': {
          '0%': { transform: 'scale(1)', boxShadow: `0 0 0 0 ${alpha(color, 0.5)}` },
          '70%': { transform: 'scale(1.03)', boxShadow: `0 0 0 7px ${alpha(color, 0)}` },
          '100%': { transform: 'scale(1)', boxShadow: `0 0 0 0 ${alpha(color, 0)}` },
        }
      };
    }
    return {};
  };

  return (
    <Tooltip 
      title={description || `${currentValue}/${targetValue} - ${Math.round(progressPercentage)}% complete`}
      arrow
      placement="top"
    >
      <Paper
        elevation={isCloseToMilestone ? 3 : 1}
        sx={{
          p: 2,
          borderRadius: 2,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          background: isCloseToMilestone 
            ? `linear-gradient(135deg, ${alpha(gradientStart, 0.1)} 0%, ${alpha(gradientEnd, 0.05)} 100%)`
            : undefined,
          borderLeft: `4px solid ${color}`,
          transition: 'all 0.3s ease',
          ...getAnimationStyle(),
          '&:hover': {
            transform: 'translateY(-3px)',
            boxShadow: theme.shadows[4]
          }
        }}
      >
        <Box
          sx={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            width: 50,
            height: 50,
            borderRadius: '50%',
            backgroundColor: alpha(color, 0.15),
            color: color,
            mb: 1.5,
            position: 'relative'
          }}
        >
          {/* Icon */}
          <Box sx={{ zIndex: 2 }}>{icon}</Box>
          
          {/* Progress circle */}
          <Box
            sx={{
              position: 'absolute',
              top: 0,
              left: 0,
              width: '100%',
              height: '100%',
              borderRadius: '50%',
              background: `conic-gradient(${color} ${progressPercentage}%, transparent 0)`,
              opacity: 0.3,
              zIndex: 1
            }}
          />
        </Box>
        
        <Typography 
          variant="h5" 
          fontWeight="bold" 
          sx={{ 
            mb: 0.5,
            color: isCloseToMilestone ? color : 'text.primary'
          }}
        >
          {currentValue}/{targetValue}
        </Typography>
        
        <Typography 
          variant="body2" 
          color="text.secondary" 
          sx={{ 
            textAlign: 'center',
            fontWeight: isCloseToMilestone ? 'medium' : 'normal'
          }}
        >
          {label}
        </Typography>
        
        {isCloseToMilestone && (
          <Box
            sx={{
              mt: 1.5,
              px: 1.5,
              py: 0.5,
              borderRadius: 1,
              backgroundColor: alpha(color, 0.1),
              border: `1px dashed ${alpha(color, 0.3)}`,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center'
            }}
          >
            <Typography 
              variant="caption" 
              sx={{ 
                color: color,
                fontWeight: 'medium',
                textAlign: 'center'
              }}
            >
              Almost there!
            </Typography>
          </Box>
        )}
      </Paper>
    </Tooltip>
  );
};

export default MilestoneApproachIndicator;
