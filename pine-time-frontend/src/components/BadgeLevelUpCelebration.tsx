import React, { useState, useEffect, useRef } from 'react';
import { Dialog, DialogContent, Typography, Box, Button, useTheme, Zoom } from '@mui/material';
import { Badge } from '../types/badges';
import LottieAnimation from './LottieAnimation';
import confettiAnimation from '../assets/animations/confetti.json';
import ArrowUpwardIcon from '@mui/icons-material/ArrowUpward';

interface BadgeLevelUpCelebrationProps {
  badge: Badge | null;
  previousLevel: number;
  open: boolean;
  onClose: () => void;
}

const BadgeLevelUpCelebration: React.FC<BadgeLevelUpCelebrationProps> = ({ 
  badge, 
  previousLevel,
  open, 
  onClose 
}) => {
  const theme = useTheme();
  const [animationStep, setAnimationStep] = useState(0);
  const lottieRef = useRef<any>(null);
  
  // Pine Time green theme color
  const pineTimeGreen = '#2E7D32';
  
  // Reset animation when dialog opens/closes
  useEffect(() => {
    if (open) {
      setAnimationStep(0);
      const timer = setTimeout(() => {
        setAnimationStep(1);
      }, 1500);
      
      return () => clearTimeout(timer);
    }
  }, [open]);
  
  // Get badge level color based on level
  const getBadgeLevelColor = (level: number) => {
    switch (level) {
      case 1: return pineTimeGreen; // Pine Time green for level 1
      case 2: return '#1976D2'; // Blue for level 2
      case 3: return '#7B1FA2'; // Purple for level 3
      case 4: return '#C62828'; // Red for level 4
      case 5: return '#F57C00'; // Orange for level 5
      default: return pineTimeGreen;
    }
  };
  
  // Get badge level name
  const getBadgeLevelName = (level: number) => {
    switch (level) {
      case 1: return 'Bronze';
      case 2: return 'Silver';
      case 3: return 'Gold';
      case 4: return 'Platinum';
      case 5: return 'Diamond';
      default: return 'Bronze';
    }
  };

  if (!badge) return null;

  return (
    <Dialog 
      open={open} 
      onClose={onClose}
      maxWidth="sm"
      fullWidth
      TransitionComponent={Zoom}
      PaperProps={{
        sx: {
          borderRadius: 4,
          overflow: 'hidden',
          position: 'relative',
          background: `linear-gradient(135deg, ${theme.palette.background.paper} 0%, ${theme.palette.background.default} 100%)`,
          boxShadow: `0 10px 30px rgba(46, 125, 50, 0.2)`,
        }
      }}
    >
      {/* Confetti animation using Lottie */}
      <Box sx={{ position: 'absolute', width: '100%', height: '100%', overflow: 'hidden', pointerEvents: 'none' }}>
        <LottieAnimation
          ref={lottieRef}
          animationData={confettiAnimation}
          loop={false}
          autoplay={true}
          style={{ width: '100%', height: '100%', position: 'absolute', top: 0, left: 0 }}
        />
      </Box>

      <DialogContent sx={{ textAlign: 'center', py: 5 }}>
        <Box
          sx={{
            position: 'relative',
            zIndex: 1
          }}
        >
          <Typography 
            variant="h4" 
            sx={{
              fontWeight: 'bold',
              mb: 2,
              textShadow: '0 2px 4px rgba(0,0,0,0.1)',
              background: `linear-gradient(90deg, ${getBadgeLevelColor(previousLevel)}, ${getBadgeLevelColor(badge.level || 1)})`,
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
            }}
          >
            🏆 Level Up! 🏆
          </Typography>
          
          {/* Badge level transition container */}
          <Box 
            sx={{ 
              my: 4, 
              display: 'flex', 
              justifyContent: 'center',
              alignItems: 'center',
              gap: 2,
              position: 'relative'
            }}
          >
            {/* Previous level badge */}
            <Box
              sx={{
                position: 'relative',
                width: 110,
                height: 110,
                borderRadius: '50%',
                background: `radial-gradient(circle at 30% 30%, ${theme.palette.mode === 'dark' ? 'rgba(255,255,255,0.2)' : 'rgba(255,255,255,0.9)'} 0%, transparent 70%)`,
                boxShadow: `
                  0 10px 25px rgba(0,0,0,0.2),
                  inset 0 -5px 10px rgba(0,0,0,0.1),
                  inset 0 5px 10px rgba(255,255,255,0.25)
                `,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                transform: animationStep === 0 ? 'scale(1)' : 'scale(0.8) translateX(-30px)',
                opacity: animationStep === 0 ? 1 : 0.7,
                transition: 'all 0.8s cubic-bezier(0.175, 0.885, 0.32, 1.275)',
                zIndex: animationStep === 0 ? 2 : 1
              }}
            >
              <Box
                component="img"
                src={badge.icon_url || '/default-badge.png'}
                alt={badge.name}
                sx={{
                  width: 80,
                  height: 80,
                  objectFit: 'contain',
                  borderRadius: '50%',
                  padding: 1,
                  background: `linear-gradient(135deg, ${getBadgeLevelColor(previousLevel)}22 0%, ${getBadgeLevelColor(previousLevel)}66 100%)`,
                  border: `3px solid ${getBadgeLevelColor(previousLevel)}`,
                }}
              />
              <Typography
                sx={{
                  position: 'absolute',
                  bottom: -10,
                  left: '50%',
                  transform: 'translateX(-50%)',
                  backgroundColor: getBadgeLevelColor(previousLevel),
                  color: '#fff',
                  fontSize: '0.75rem',
                  fontWeight: 'bold',
                  px: 1.5,
                  py: 0.3,
                  borderRadius: 10,
                  whiteSpace: 'nowrap',
                  boxShadow: 1
                }}
              >
                {getBadgeLevelName(previousLevel)}
              </Typography>
            </Box>
            
            {/* Arrow animation */}
            <Box
              sx={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                opacity: animationStep === 0 ? 0 : 1,
                transform: animationStep === 0 ? 'scale(0.5)' : 'scale(1)',
                transition: 'all 0.5s ease 0.3s',
              }}
            >
              <ArrowUpwardIcon 
                sx={{ 
                  fontSize: 40, 
                  color: pineTimeGreen,
                  animation: 'pulse 1.5s infinite',
                  '@keyframes pulse': {
                    '0%': { transform: 'scale(1)', opacity: 0.7 },
                    '50%': { transform: 'scale(1.2)', opacity: 1 },
                    '100%': { transform: 'scale(1)', opacity: 0.7 },
                  }
                }} 
              />
            </Box>
            
            {/* New level badge */}
            <Box
              sx={{
                position: 'relative',
                width: 110,
                height: 110,
                borderRadius: '50%',
                background: `radial-gradient(circle at 30% 30%, ${theme.palette.mode === 'dark' ? 'rgba(255,255,255,0.2)' : 'rgba(255,255,255,0.9)'} 0%, transparent 70%)`,
                boxShadow: `
                  0 10px 25px rgba(0,0,0,0.2),
                  inset 0 -5px 10px rgba(0,0,0,0.1),
                  inset 0 5px 10px rgba(255,255,255,0.25)
                `,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                transform: animationStep === 0 ? 'scale(0.8) translateX(30px)' : 'scale(1.1) translateX(30px)',
                opacity: animationStep === 0 ? 0.5 : 1,
                transition: 'all 0.8s cubic-bezier(0.175, 0.885, 0.32, 1.275)',
                zIndex: animationStep === 0 ? 1 : 2,
                animation: animationStep === 1 ? 'glow 2s infinite' : 'none',
                '@keyframes glow': {
                  '0%': { boxShadow: `0 10px 25px rgba(0,0,0,0.2), 0 0 15px ${getBadgeLevelColor(badge.level || 1)}55` },
                  '50%': { boxShadow: `0 10px 25px rgba(0,0,0,0.2), 0 0 30px ${getBadgeLevelColor(badge.level || 1)}88` },
                  '100%': { boxShadow: `0 10px 25px rgba(0,0,0,0.2), 0 0 15px ${getBadgeLevelColor(badge.level || 1)}55` },
                }
              }}
            >
              <Box
                component="img"
                src={badge.icon_url || '/default-badge.png'}
                alt={badge.name}
                sx={{
                  width: 80,
                  height: 80,
                  objectFit: 'contain',
                  borderRadius: '50%',
                  padding: 1,
                  background: `linear-gradient(135deg, ${getBadgeLevelColor(badge.level || 1)}22 0%, ${getBadgeLevelColor(badge.level || 1)}66 100%)`,
                  border: `3px solid ${getBadgeLevelColor(badge.level || 1)}`,
                }}
              />
              <Typography
                sx={{
                  position: 'absolute',
                  bottom: -10,
                  left: '50%',
                  transform: 'translateX(-50%)',
                  backgroundColor: getBadgeLevelColor(badge.level || 1),
                  color: '#fff',
                  fontSize: '0.75rem',
                  fontWeight: 'bold',
                  px: 1.5,
                  py: 0.3,
                  borderRadius: 10,
                  whiteSpace: 'nowrap',
                  boxShadow: 1
                }}
              >
                {getBadgeLevelName(badge.level || 1)}
              </Typography>
            </Box>
          </Box>
          
          <Typography 
            variant="h5" 
            sx={{ 
              fontWeight: 'bold',
              mb: 1,
              opacity: animationStep === 0 ? 0 : 1,
              transform: animationStep === 0 ? 'translateY(20px)' : 'translateY(0)',
              transition: 'all 0.5s ease 0.5s',
            }}
          >
            {badge.name} Badge Upgraded!
          </Typography>
          
          <Typography 
            variant="body1" 
            color="text.secondary" 
            sx={{ 
              maxWidth: '80%', 
              mx: 'auto', 
              mb: 3,
              lineHeight: 1.6,
              opacity: animationStep === 0 ? 0 : 1,
              transform: animationStep === 0 ? 'translateY(20px)' : 'translateY(0)',
              transition: 'all 0.5s ease 0.7s',
            }}
          >
            {badge.description}
          </Typography>
          
          <Box
            sx={{
              opacity: animationStep === 0 ? 0 : 1,
              transform: animationStep === 0 ? 'translateY(20px)' : 'translateY(0)',
              transition: 'all 0.5s ease 0.9s',
            }}
          >
            <Button
              variant="contained"
              color="primary"
              size="large"
              onClick={onClose}
              sx={{ 
                mt: 2,
                px: 4,
                py: 1.2,
                borderRadius: 8,
                fontWeight: 'bold',
                boxShadow: `0 4px 10px ${getBadgeLevelColor(badge.level || 1)}66`,
                background: `linear-gradient(90deg, ${theme.palette.primary.main}, ${getBadgeLevelColor(badge.level || 1)})`,
                transition: 'all 0.3s ease',
                '&:hover': {
                  boxShadow: `0 6px 15px ${getBadgeLevelColor(badge.level || 1)}88`,
                  transform: 'translateY(-2px)'
                }
              }}
            >
              Awesome!
            </Button>
          </Box>
        </Box>
      </DialogContent>
    </Dialog>
  );
};

export default BadgeLevelUpCelebration;
