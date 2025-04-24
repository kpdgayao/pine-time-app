import React, { useEffect, useState } from 'react';
import { Dialog, DialogContent, Typography, Box, Button, useTheme } from '@mui/material';
import LocalFireDepartmentIcon from '@mui/icons-material/LocalFireDepartment';

interface StreakCelebrationProps {
  streakCount: number;
  open: boolean;
  onClose: () => void;
}

const StreakCelebration: React.FC<StreakCelebrationProps> = ({ 
  streakCount, 
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

  // Pine Time green theme color
  const pineTimeGreen = '#2E7D32';

  // Generate confetti pieces when the dialog opens
  useEffect(() => {
    if (open) {
      const colors = [
        theme.palette.primary.main,
        theme.palette.primary.light,
        theme.palette.secondary.main,
        theme.palette.secondary.light,
        '#FFC107', // amber
        pineTimeGreen, // Pine Time green
        '#FF5722', // deep orange (fire color)
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
          <Typography variant="h4" color="warning.main" gutterBottom>
            🔥 Impressive Streak! 🔥
          </Typography>
          
          <Box sx={{ my: 3, display: 'flex', justifyContent: 'center' }}>
            <Box
              sx={{
                width: 120,
                height: 120,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                borderRadius: '50%',
                backgroundColor: 'warning.light',
                color: 'warning.dark',
                p: 1,
                boxShadow: `0 0 20px ${theme.palette.warning.main}`,
                animation: 'pulse 2s infinite',
                '@keyframes pulse': {
                  '0%': { boxShadow: `0 0 0 0 rgba(255, 152, 0, 0.7)` },
                  '70%': { boxShadow: `0 0 0 15px rgba(255, 152, 0, 0)` },
                  '100%': { boxShadow: `0 0 0 0 rgba(255, 152, 0, 0)` },
                },
              }}
            >
              <LocalFireDepartmentIcon sx={{ fontSize: 80 }} />
            </Box>
          </Box>
          
          <Typography variant="h5" gutterBottom>
            <strong>{streakCount} Week Streak!</strong>
          </Typography>
          
          <Typography variant="body1" color="text.secondary" paragraph>
            You've been consistently attending events for {streakCount} weeks in a row! Keep up the great work to earn more rewards.
          </Typography>
          
          <Button
            variant="contained"
            color="warning"
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
            Keep the Streak Going!
          </Button>
        </Box>
      </DialogContent>
    </Dialog>
  );
};

export default StreakCelebration;
