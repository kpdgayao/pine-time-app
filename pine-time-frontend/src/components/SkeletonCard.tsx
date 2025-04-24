import React from 'react';
import { Box, Skeleton } from '@mui/material';
import PineTimeCard from './PineTimeCard';
import { styled, keyframes } from '@mui/material/styles';

// Create a pulsing animation
const pulse = keyframes`
  0% {
    opacity: 0.6;
  }
  50% {
    opacity: 0.8;
  }
  100% {
    opacity: 0.6;
  }
`;

const AnimatedSkeleton = styled(Skeleton)(({ theme }) => ({
  animation: `${pulse} 1.5s ease-in-out infinite`,
  backgroundColor: theme.palette.mode === 'light' ? 'rgba(0, 0, 0, 0.08)' : 'rgba(255, 255, 255, 0.08)',
  '&::after': {
    background: `linear-gradient(90deg, transparent, ${
      theme.palette.mode === 'light' ? 'rgba(0, 0, 0, 0.04)' : 'rgba(255, 255, 255, 0.04)'
    }, transparent)`,
  },
}));

interface SkeletonCardProps {
  type?: 'event' | 'profile' | 'badge' | 'leaderboard';
  height?: number;
  width?: number | string;
  sx?: any;
}

const SkeletonCard: React.FC<SkeletonCardProps> = ({
  type = 'event',
  height,
  width,
  sx = {},
}) => {
  // Different skeleton layouts based on type
  const renderContent = () => {
    switch (type) {
      case 'event':
        return (
          <>
            <AnimatedSkeleton 
              variant="rectangular" 
              width="100%" 
              height={180} 
              sx={{ borderTopLeftRadius: 12, borderTopRightRadius: 12 }} 
            />
            <Box sx={{ p: 2 }}>
              <AnimatedSkeleton variant="text" width="70%" height={32} sx={{ mb: 1 }} />
              <AnimatedSkeleton variant="text" width="40%" height={24} sx={{ mb: 1 }} />
              <Box sx={{ display: 'flex', gap: 1, mb: 1 }}>
                <AnimatedSkeleton variant="rectangular" width={60} height={24} sx={{ borderRadius: 4 }} />
                <AnimatedSkeleton variant="rectangular" width={80} height={24} sx={{ borderRadius: 4 }} />
              </Box>
              <AnimatedSkeleton variant="text" width="90%" height={20} sx={{ mb: 1 }} />
              <AnimatedSkeleton variant="text" width="85%" height={20} sx={{ mb: 1 }} />
              <AnimatedSkeleton variant="rectangular" width="100%" height={36} sx={{ mt: 2, borderRadius: 2 }} />
            </Box>
          </>
        );
      
      case 'profile':
        return (
          <Box sx={{ p: 2 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
              <AnimatedSkeleton variant="circular" width={64} height={64} />
              <Box sx={{ ml: 2, flex: 1 }}>
                <AnimatedSkeleton variant="text" width="60%" height={28} />
                <AnimatedSkeleton variant="text" width="40%" height={20} />
              </Box>
            </Box>
            <AnimatedSkeleton variant="rectangular" width="100%" height={100} sx={{ borderRadius: 2, mb: 2 }} />
            <AnimatedSkeleton variant="text" width="90%" height={20} sx={{ mb: 1 }} />
            <AnimatedSkeleton variant="text" width="80%" height={20} sx={{ mb: 1 }} />
            <AnimatedSkeleton variant="text" width="70%" height={20} sx={{ mb: 1 }} />
          </Box>
        );
      
      case 'badge':
        return (
          <Box sx={{ p: 2, display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
            <AnimatedSkeleton variant="circular" width={80} height={80} sx={{ mb: 2 }} />
            <AnimatedSkeleton variant="text" width="70%" height={24} sx={{ mb: 1 }} />
            <AnimatedSkeleton variant="text" width="90%" height={16} sx={{ mb: 1 }} />
            <AnimatedSkeleton variant="rectangular" width="80%" height={8} sx={{ borderRadius: 4, mb: 2 }} />
          </Box>
        );
      
      case 'leaderboard':
        return (
          <Box sx={{ p: 2 }}>
            <AnimatedSkeleton variant="text" width="50%" height={32} sx={{ mb: 2 }} />
            {[...Array(5)].map((_, idx) => (
              <Box key={idx} sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <AnimatedSkeleton variant="circular" width={40} height={40} sx={{ mr: 2 }} />
                <Box sx={{ flex: 1 }}>
                  <AnimatedSkeleton variant="text" width="60%" height={20} />
                  <AnimatedSkeleton variant="text" width="30%" height={16} />
                </Box>
                <AnimatedSkeleton variant="text" width={60} height={24} />
              </Box>
            ))}
          </Box>
        );
      
      default:
        return (
          <Box sx={{ p: 2 }}>
            <AnimatedSkeleton variant="rectangular" width="100%" height={150} sx={{ borderRadius: 2, mb: 2 }} />
            <AnimatedSkeleton variant="text" width="70%" height={24} sx={{ mb: 1 }} />
            <AnimatedSkeleton variant="text" width="90%" height={20} sx={{ mb: 1 }} />
          </Box>
        );
    }
  };

  return (
    <PineTimeCard
      elevation={1}
      sx={{
        width: width || { xs: '100%', sm: 'calc(50% - 16px)', md: 'calc(33.333% - 16px)' },
        height: height || 'auto',
        minHeight: type === 'event' ? 350 : 200,
        overflow: 'hidden',
        borderRadius: 3,
        ...sx,
      }}
    >
      {renderContent()}
    </PineTimeCard>
  );
};

export default React.memo(SkeletonCard);
