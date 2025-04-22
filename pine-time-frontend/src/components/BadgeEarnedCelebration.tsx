import React, { useState, useEffect } from 'react';
import { Dialog, DialogContent, Typography, Box, Button, useTheme } from '@mui/material';
import { Badge } from '../types/badges';

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
  const [confetti, setConfetti] = useState<Array<{
    left: string;
    width: string;
    height: string;
    backgroundColor: string;
    transform: string;
    opacity: number;
    delay: string;
  }>>([]);

  // Generate confetti pieces when the dialog opens
  useEffect(() => {
    if (open) {
      const colors = [
        theme.palette.primary.main,
        theme.palette.primary.light,
        theme.palette.secondary.main,
        theme.palette.secondary.light,
        '#FFC107', // amber
        '#4CAF50', // green
        '#2196F3', // blue
      ];
      
      const newConfetti = Array.from({ length: 50 }).map(() => {
        const left = `${Math.random() * 100}%`;
        const width = `${Math.random() * 10 + 5}px`;
        const height = `${Math.random() * 10 + 5}px`;
        const backgroundColor = colors[Math.floor(Math.random() * colors.length)];
        const transform = `rotate(${Math.random() * 360}deg)`;
        const opacity = Math.random() * 0.8 + 0.2;
        const delay = `${Math.random() * 3}s`;
        
        return {
          left,
          width,
          height,
          backgroundColor,
          transform,
          opacity,
          delay,
        };
      });
      
      setConfetti(newConfetti);
    } else {
      setConfetti([]);
    }
  }, [open, theme]);

  if (!badge) return null;

  return (
    <Dialog 
      open={open} 
      onClose={onClose}
      maxWidth="sm"
      fullWidth
      PaperProps={{
        sx: {
          borderRadius: 4,
          overflow: 'hidden',
          position: 'relative',
          background: `linear-gradient(135deg, ${theme.palette.background.paper} 0%, ${theme.palette.background.default} 100%)`,
        }
      }}
    >
      {/* Confetti animation */}
      <Box sx={{ position: 'absolute', width: '100%', height: '100%', overflow: 'hidden', pointerEvents: 'none' }}>
        {confetti.map((piece, index) => (
          <Box
            key={index}
            sx={{
              position: 'absolute',
              left: piece.left,
              top: '-20px',
              width: piece.width,
              height: piece.height,
              backgroundColor: piece.backgroundColor,
              transform: piece.transform,
              opacity: piece.opacity,
              animation: `fall 3s linear ${piece.delay} forwards`,
              '@keyframes fall': {
                '0%': {
                  top: '-20px',
                  transform: `${piece.transform} translateY(0) rotate(0deg)`,
                },
                '100%': {
                  top: 'calc(100% + 20px)',
                  transform: `${piece.transform} translateY(0) rotate(720deg)`,
                },
              },
            }}
          />
        ))}
      </Box>

      <DialogContent sx={{ textAlign: 'center', py: 5 }}>
        <Box
          sx={{
            animation: 'pop 0.5s ease-out',
            '@keyframes pop': {
              '0%': { transform: 'scale(0.5)', opacity: 0 },
              '80%': { transform: 'scale(1.1)' },
              '100%': { transform: 'scale(1)', opacity: 1 },
            },
          }}
        >
          <Typography variant="h4" color="primary" gutterBottom>
            🎉 Congratulations! 🎉
          </Typography>
          
          <Box sx={{ my: 3, display: 'flex', justifyContent: 'center' }}>
            <Box
              component="img"
              src={badge.icon_url || '/default-badge.png'}
              alt={badge.name}
              sx={{
                width: 120,
                height: 120,
                objectFit: 'contain',
                borderRadius: '50%',
                p: 1,
                boxShadow: `0 0 20px ${theme.palette.primary.main}`,
                animation: 'pulse 2s infinite',
                '@keyframes pulse': {
                  '0%': { boxShadow: `0 0 0 0 rgba(46, 125, 50, 0.7)` },
                  '70%': { boxShadow: `0 0 0 15px rgba(46, 125, 50, 0)` },
                  '100%': { boxShadow: `0 0 0 0 rgba(46, 125, 50, 0)` },
                },
              }}
            />
          </Box>
          
          <Typography variant="h5" gutterBottom>
            You've earned the <strong>{badge.name}</strong> badge!
            {badge.level && <span> (Level {badge.level})</span>}
          </Typography>
          
          <Typography variant="body1" color="text.secondary" paragraph>
            {badge.description}
          </Typography>
          
          <Button
            variant="contained"
            color="primary"
            size="large"
            onClick={onClose}
            sx={{ 
              mt: 2,
              px: 4,
              borderRadius: 8,
              fontWeight: 'bold',
              boxShadow: 3,
              '&:hover': {
                boxShadow: 5,
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
