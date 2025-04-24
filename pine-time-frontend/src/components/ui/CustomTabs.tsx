import React, { useState, useEffect } from 'react';
import { Box, ButtonBase, Typography, useTheme, alpha } from '@mui/material';

interface TabOption {
  value: string;
  label: string;
}

interface CustomTabsProps {
  options: TabOption[];
  value: string;
  onChange: (value: string) => void;
  color?: 'primary' | 'secondary' | 'warning' | 'info';
}

const CustomTabs: React.FC<CustomTabsProps> = ({ 
  options, 
  value, 
  onChange,
  color = 'primary'
}) => {
  const theme = useTheme();
  const [indicatorStyle, setIndicatorStyle] = useState({
    left: '0px',
    width: '0px',
  });
  const [activeTabRef, setActiveTabRef] = useState<HTMLElement | null>(null);

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

  // Update indicator position when active tab changes
  useEffect(() => {
    if (activeTabRef) {
      setIndicatorStyle({
        left: `${activeTabRef.offsetLeft}px`,
        width: `${activeTabRef.offsetWidth}px`,
      });
    }
  }, [activeTabRef, value]);

  return (
    <Box
      sx={{
        position: 'relative',
        display: 'flex',
        backgroundColor: alpha(getColorValue(), 0.05),
        borderRadius: 2,
        p: 0.5,
        boxShadow: `0 2px 8px ${alpha(getColorValue(), 0.1)}`,
      }}
    >
      {/* Sliding indicator */}
      <Box
        sx={{
          position: 'absolute',
          height: 'calc(100% - 8px)',
          top: '4px',
          borderRadius: 1.5,
          backgroundColor: alpha(getColorValue(), 0.15),
          transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
          boxShadow: `0 2px 5px ${alpha(getColorValue(), 0.2)}`,
          border: `1px solid ${alpha(getColorValue(), 0.3)}`,
          zIndex: 0,
          ...indicatorStyle
        }}
      />

      {/* Tab buttons */}
      {options.map((option) => (
        <ButtonBase
          key={option.value}
          ref={(el) => {
            if (option.value === value) {
              setActiveTabRef(el);
            }
          }}
          onClick={() => onChange(option.value)}
          sx={{
            flex: 1,
            py: 1,
            px: 2,
            borderRadius: 1.5,
            position: 'relative',
            zIndex: 1,
            transition: 'all 0.2s ease',
            color: option.value === value 
              ? getColorValue()
              : theme.palette.text.secondary,
            fontWeight: option.value === value ? 600 : 400,
            '&:hover': {
              backgroundColor: option.value !== value 
                ? alpha(getColorValue(), 0.05)
                : 'transparent',
            }
          }}
        >
          <Typography 
            variant="button" 
            sx={{ 
              fontWeight: 'inherit',
              textTransform: 'none',
              fontSize: '0.9rem',
              letterSpacing: 0.5
            }}
          >
            {option.label}
          </Typography>
        </ButtonBase>
      ))}
    </Box>
  );
};

export default CustomTabs;
