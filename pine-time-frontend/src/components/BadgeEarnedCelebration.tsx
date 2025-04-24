import React, { useState, useEffect, useRef } from 'react';
import { Dialog, DialogContent, Typography, Box, Button, useTheme, Zoom } from '@mui/material';
import { Badge } from '../types/badges';
import LottieAnimation from '../components/LottieAnimation';
import confettiAnimation from '../assets/animations/confetti.json';
import badgeShineAnimation from '../assets/animations/badge-shine.json';

interface BadgeEarnedCelebrationProps {
  badge: Badge | null;
  open: boolean;
  onClose: () => void;
}

const BadgeEarnedCelebration: React.FC<BadgeEarnedCelebrationProps> = ({ 
  badge, 
  open, 
  onClose 
}) => {
  const theme = useTheme();
  const [showBadgeShine, setShowBadgeShine] = useState(false);
  const lottieRef = useRef<any>(null);
  const badgeShineRef = useRef<any>(null);
  
  // Pine Time green theme color
  const pineTimeGreen = '#2E7D32';
  
  // Reset animation states when dialog opens/closes
  useEffect(() => {
    if (open) {
      // Start badge shine animation after a delay
      const timer = setTimeout(() => {
        setShowBadgeShine(true);
      }, 1000);
      
      return () => clearTimeout(timer);
    } else {
      setShowBadgeShine(false);
    }
  }, [open]);
  
  // Get badge level color based on level
  const getBadgeLevelColor = () => {
    if (!badge?.level) return pineTimeGreen;
    
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
    if (!badge?.level) return 'Bronze';
    
    switch (badge.level) {
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
          onComplete={() => {/* Animation complete */}}
        />
      </Box>

      <DialogContent sx={{ textAlign: 'center', py: 5 }}>
        <Box
          sx={{
            animation: 'pop 0.7s cubic-bezier(0.175, 0.885, 0.32, 1.275)',
            '@keyframes pop': {
              '0%': { transform: 'scale(0.5)', opacity: 0 },
              '70%': { transform: 'scale(1.1)' },
              '90%': { transform: 'scale(0.95)' },
              '100%': { transform: 'scale(1)', opacity: 1 },
            },
            position: 'relative',
            zIndex: 1
          }}
        >
          <Typography 
            variant="h4" 
            sx={{
              color: getBadgeLevelColor(),
              fontWeight: 'bold',
              mb: 2,
              textShadow: '0 2px 4px rgba(0,0,0,0.1)',
              animation: 'shimmer 2s infinite linear',
              '@keyframes shimmer': {
                '0%': { opacity: 0.8 },
                '50%': { opacity: 1 },
                '100%': { opacity: 0.8 },
              }
            }}
          >
            🎉 Achievement Unlocked! 🎉
          </Typography>
          
          {/* Badge container with shine effect */}
          <Box 
            sx={{ 
              my: 4, 
              display: 'flex', 
              justifyContent: 'center',
              position: 'relative'
            }}
          >
            {/* Badge shine animation */}
            {showBadgeShine && (
              <Box sx={{ position: 'absolute', width: '150px', height: '150px', zIndex: 2 }}>
                <LottieAnimation
                  ref={badgeShineRef}
                  animationData={badgeShineAnimation}
                  loop={true}
                  autoplay={true}
                  style={{ width: '100%', height: '100%' }}
                />
              </Box>
            )}
            
            {/* Badge image with 3D effect */}
            <Box
              sx={{
                position: 'relative',
                zIndex: 1,
                width: 140,
                height: 140,
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
                transform: 'perspective(800px) rotateY(0deg)',
                transition: 'transform 0.5s ease',
                animation: 'float 3s ease-in-out infinite',
                '@keyframes float': {
                  '0%': { transform: 'perspective(800px) rotateY(0deg) translateY(0px)' },
                  '50%': { transform: 'perspective(800px) rotateY(5deg) translateY(-10px)' },
                  '100%': { transform: 'perspective(800px) rotateY(0deg) translateY(0px)' },
                },
                '&:hover': {
                  transform: 'perspective(800px) rotateY(10deg)'
                }
              }}
            >
              <Box
                component="img"
                src={badge?.icon_url || '/default-badge.png'}
                alt={badge?.name}
                sx={{
                  width: 110,
                  height: 110,
                  objectFit: 'contain',
                  borderRadius: '50%',
                  padding: 1,
                  background: `linear-gradient(135deg, ${getBadgeLevelColor()}22 0%, ${getBadgeLevelColor()}66 100%)`,
                  border: `3px solid ${getBadgeLevelColor()}`,
                }}
              />
            </Box>
          </Box>
          
          <Typography 
            variant="h5" 
            sx={{ 
              fontWeight: 'bold',
              mb: 1,
              background: `linear-gradient(90deg, ${theme.palette.primary.main}, ${getBadgeLevelColor()})`,
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              textShadow: '0 2px 4px rgba(0,0,0,0.05)',
            }}
          >
            <Box component="span" sx={{ display: 'block', mb: 0.5 }}>
              {badge?.name}
            </Box>
            {badge?.level && (
              <Box 
                component="span" 
                sx={{ 
                  display: 'inline-block',
                  fontSize: '0.8em',
                  px: 2,
                  py: 0.5,
                  borderRadius: 2,
                  background: `linear-gradient(90deg, ${getBadgeLevelColor()}66, ${getBadgeLevelColor()}33)`,
                  color: getBadgeLevelColor(),
                  boxShadow: `0 2px 4px ${getBadgeLevelColor()}33`,
                  WebkitBackgroundClip: 'initial',
                  WebkitTextFillColor: 'initial',
                }}
              >
                {getBadgeLevelName()} Level {badge.level}
              </Box>
            )}
          </Typography>
          
          <Typography 
            variant="body1" 
            color="text.secondary" 
            sx={{ 
              maxWidth: '80%', 
              mx: 'auto', 
              mb: 3,
              lineHeight: 1.6,
              animation: 'fadeIn 1s ease-in',
              '@keyframes fadeIn': {
                '0%': { opacity: 0, transform: 'translateY(10px)' },
                '100%': { opacity: 1, transform: 'translateY(0)' },
              }
            }}
          >
            {badge?.description}
          </Typography>
          
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
              boxShadow: `0 4px 10px ${getBadgeLevelColor()}66`,
              background: `linear-gradient(90deg, ${theme.palette.primary.main}, ${getBadgeLevelColor()})`,
              transition: 'all 0.3s ease',
              '&:hover': {
                boxShadow: `0 6px 15px ${getBadgeLevelColor()}88`,
                transform: 'translateY(-2px)'
              }
            }}
          >
            Awesome!
          </Button>
        </Box>
      </DialogContent>
    </Dialog>
  );
};

export default BadgeEarnedCelebration;
