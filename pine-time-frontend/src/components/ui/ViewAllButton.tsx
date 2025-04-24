import React from 'react';
import { Button, Typography, useTheme, alpha } from '@mui/material';
import ArrowForwardIcon from '@mui/icons-material/ArrowForward';

interface ViewAllButtonProps {
  onClick: () => void;
  label?: string;
  color?: 'primary' | 'secondary' | 'warning' | 'info';
  size?: 'small' | 'medium' | 'large';
  fullWidth?: boolean;
}

const ViewAllButton: React.FC<ViewAllButtonProps> = ({ 
  onClick, 
  label = 'View All', 
  color = 'primary',
  size = 'medium',
  fullWidth = false
}) => {
  const theme = useTheme();
  
  // Pine Time green theme color
  const pineTimeGreen = '#2E7D32';
  
  const getColorValue = () => {
    switch (color) {
      case 'primary': return theme.palette.primary.main;
      case 'secondary': return theme.palette.secondary.main;
      case 'warning': return theme.palette.warning.main;
      case 'info': return theme.palette.info.main;
      default: return pineTimeGreen; // Default to Pine Time green
    }
  };
  
  const getPadding = () => {
    switch (size) {
      case 'small': return { px: 1.5, py: 0.5 };
      case 'large': return { px: 3, py: 1 };
      default: return { px: 2, py: 0.75 };
    }
  };
  
  const getFontSize = () => {
    switch (size) {
      case 'small': return '0.75rem';
      case 'large': return '0.95rem';
      default: return '0.85rem';
    }
  };

  return (
    <Button
      onClick={onClick}
      fullWidth={fullWidth}
      sx={{
        ...getPadding(),
        borderRadius: 2,
        backgroundColor: 'transparent',
        color: getColorValue(),
        border: `1px solid ${alpha(getColorValue(), 0.3)}`,
        transition: 'all 0.2s ease',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        gap: 0.5,
        '&:hover': {
          backgroundColor: alpha(getColorValue(), 0.08),
          transform: 'translateY(-2px)',
          boxShadow: `0 4px 8px -2px ${alpha(getColorValue(), 0.2)}`,
          '& .arrow-icon': {
            transform: 'translateX(3px)',
          }
        },
        '&:active': {
          transform: 'translateY(0)',
          boxShadow: 'none',
        }
      }}
    >
      <Typography 
        variant="button" 
        sx={{ 
          fontSize: getFontSize(),
          fontWeight: 600,
          letterSpacing: 0.5,
          textTransform: 'none'
        }}
      >
        {label}
      </Typography>
      <ArrowForwardIcon 
        className="arrow-icon" 
        fontSize="small" 
        sx={{ 
          transition: 'transform 0.2s ease',
          fontSize: getFontSize()
        }} 
      />
    </Button>
  );
};

export default ViewAllButton;
